"""Fábrica y rutas de lectura para la API pública del INPC."""

from collections.abc import Generator
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from hashlib import sha256
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from sqlalchemy import Connection, Engine, and_, func, select, text
from sqlalchemy.exc import SQLAlchemyError

from inflacion_lab.config import ConfigurationError, Settings
from inflacion_lab.db.conexion import create_engine
from inflacion_lab.db.metricas import Medida, ResultadoMetrica, serie_metricas
from inflacion_lab.db.tablas import ejecuciones_etl, geografias, observaciones, rubros, series

MAX_MONTHS = 240
DEFAULT_HISTORY_MONTHS = 60
_FUENTE_URL = "https://www.inegi.org.mx/temas/inpc/"
_RATE_QUANTUM = Decimal("0.000001")


class ApiError(Exception):
    """Error público, sin detalles internos de conexión o SQL."""

    def __init__(
        self, status_code: int, codigo: str, mensaje: str, detalles: object = None
    ) -> None:
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles


def create_app(*, settings: Settings | None = None, engine: Engine | None = None) -> FastAPI:
    """Crea la aplicación sin abrir una conexión ni exigir credenciales al importar."""
    app = FastAPI(title="Laboratorio de inflación", version="1.0.0")
    app.state.settings = Settings.from_env() if settings is None else settings
    app.state.engine = engine
    router = APIRouter(prefix=app.state.settings.api_prefix)

    @app.exception_handler(ApiError)
    def handle_api_error(_: Request, error: ApiError) -> JSONResponse:
        content: dict[str, object] = {"codigo": error.codigo, "mensaje": error.mensaje}
        if error.detalles is not None:
            content["detalles"] = error.detalles
        return JSONResponse(status_code=error.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    def handle_validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "parametros_invalidos",
                "mensaje": "Los parámetros de la solicitud no son válidos.",
                "detalles": jsonable_encoder(error.errors()),
            },
        )

    def connection() -> Generator[Connection, None, None]:
        active_engine = app.state.engine
        if active_engine is None:
            try:
                active_engine = create_engine(app.state.settings.database_url("api"))
            except ConfigurationError as error:
                raise ApiError(
                    503, "base_no_disponible", "La base de datos no está disponible."
                ) from error
            app.state.engine = active_engine
        try:
            with active_engine.connect() as db:
                db.execute(text("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
                try:
                    yield db
                finally:
                    db.rollback()
        except SQLAlchemyError as error:
            raise ApiError(
                503, "base_no_disponible", "La base de datos no está disponible."
            ) from error

    Database = Annotated[Connection, Depends(connection)]

    @router.get("/health/live", tags=["salud"])
    def live() -> dict[str, str]:
        return {"estado": "activo"}

    @router.get("/health/ready", tags=["salud"])
    def ready(db: Database) -> dict[str, str]:
        version = db.scalar(text("SELECT version_num FROM alembic_version"))
        if version != "20261026_01":
            raise ApiError(503, "esquema_no_disponible", "El esquema de datos no es compatible.")
        return {"estado": "listo"}

    @router.get("/catalogo", tags=["consulta"])
    def catalog(request: Request, db: Database) -> Response:
        publication = _publication(db)
        geography_rows = db.execute(select(geografias).order_by(geografias.c.id)).mappings().all()
        rubro_rows = db.execute(select(rubros).order_by(rubros.c.orden)).mappings().all()
        coverage = (
            select(
                series.c.geografia_id,
                series.c.rubro_id,
                series.c.id_serie_inegi,
                series.c.referencia_indice,
                func.min(observaciones.c.periodo).label("periodo_min"),
                func.max(observaciones.c.periodo).label("periodo_max"),
            )
            .outerjoin(observaciones, observaciones.c.serie_id == series.c.id)
            .group_by(
                series.c.geografia_id,
                series.c.rubro_id,
                series.c.id_serie_inegi,
                series.c.referencia_indice,
            )
            .order_by(series.c.geografia_id, series.c.rubro_id)
        )
        series_rows = db.execute(coverage).mappings().all()
        source_max = max((row.periodo_max for row in series_rows if row.periodo_max), default=None)
        data = {
            "geografias": [_geografia(row) for row in geography_rows],
            "rubros": [
                {"id": row.id, "nombre": row.etiqueta_fuente, "orden": row.orden}
                for row in rubro_rows
            ],
            "series": [
                {
                    "geografia": row.geografia_id,
                    "rubro": row.rubro_id,
                    "id_serie_inegi": row.id_serie_inegi,
                    "base": row.referencia_indice,
                    "periodo_min": _month(row.periodo_min),
                    "periodo_max": _month(row.periodo_max),
                }
                for row in series_rows
            ],
        }
        return _response(request, data, _meta(publication, periodo_fuente_max=_month(source_max)))

    @router.get("/resumen", tags=["consulta"])
    def summary(
        request: Request,
        geografia: str,
        db: Database,
        periodo: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
    ) -> Response:
        publication = _publication(db)
        geography = _require_geography(db, geografia)
        if publication is None:
            return _response(request, _empty_summary(), _meta(None, geografia=geography.id))
        serie_id = _require_series(db, geography.id, "general")
        source_max = _source_max(db, serie_id)
        selected = _select_period(periodo, source_max)
        if selected is None:
            return _response(request, _empty_summary(), _meta(publication, geografia=geography.id))
        values = _metrics_at_period(db, serie_id, selected)
        data = {
            "periodo": _month(selected),
            "indice": _measurement(values["indice"]),
            "mensual": _measurement(values["mensual"]),
            "anual": _measurement(values["anual"]),
        }
        state = (
            "disponible"
            if any(item.estado == "disponible" for item in values.values())
            else "sin_datos"
        )
        return _response(
            request,
            data,
            _meta(
                publication,
                geografia=geography.id,
                periodo_consulta=_month(selected),
                periodo_fuente_max=_month(source_max),
                estado=state,
            ),
        )

    @router.get("/series", tags=["consulta"])
    def history(
        request: Request,
        geografia: str,
        rubro: str,
        db: Database,
        medida: Medida = "anual",
        desde: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
        hasta: Annotated[str | None, Query(pattern=r"^\d{4}-\d{2}$")] = None,
    ) -> Response:
        publication = _publication(db)
        geography = _require_geography(db, geografia)
        _require_rubro(db, rubro)
        if publication is None:
            return _response(
                request,
                [],
                _meta(None, geografia=geography.id, rubro=rubro, medida=medida),
            )
        serie_id = _require_series(db, geography.id, rubro)
        source_max = _source_max(db, _require_series(db, geography.id, "general"))
        start, end = _history_range(desde, hasta, source_max)
        rows = {
            item.periodo: item
            for item in serie_metricas(db, serie_id=serie_id, medida=medida, desde=start, hasta=end)
        }
        data = [
            _measurement(rows.get(month, _missing_metric(month, medida)), include_period=True)
            for month in _months(start, end)
        ]
        state = "disponible" if any(row["estado"] == "disponible" for row in data) else "sin_datos"
        return _response(
            request,
            data,
            _meta(
                publication,
                geografia=geography.id,
                rubro=rubro,
                medida=medida,
                desde=_month(start),
                hasta=_month(end),
                periodo_fuente_max=_month(source_max),
                estado=state,
            ),
        )

    app.include_router(router)
    return app


def _publication(db: Connection) -> Any | None:
    return db.execute(
        select(ejecuciones_etl.c.id, ejecuciones_etl.c.finalizada_en)
        .where(ejecuciones_etl.c.estado == "exitosa")
        .where(ejecuciones_etl.c.finalizada_en.is_not(None))
        .order_by(ejecuciones_etl.c.finalizada_en.desc())
        .limit(1)
    ).one_or_none()


def _meta(
    publication: Any | None, *, estado: str | None = None, **selection: object
) -> dict[str, object]:
    meta: dict[str, object] = {
        "estado": estado or ("disponible" if publication else "sin_publicacion"),
        "version_datos": str(publication.id) if publication else None,
        "ultima_carga_exitosa": publication.finalizada_en.isoformat() if publication else None,
        "fuente": "INEGI",
        "fuente_url": _FUENTE_URL,
    }
    meta.update({key: value for key, value in selection.items() if value is not None})
    return meta


def _response(request: Request, data: object, meta: dict[str, object]) -> Response:
    normalized_query = "&".join(
        f"{key}={value}" for key, value in sorted(request.query_params.items())
    )
    tag = sha256(
        f"{request.url.path}?{normalized_query}|{meta['version_datos']}".encode()
    ).hexdigest()
    etag = f'"{tag}"'
    headers = {"Cache-Control": "public, max-age=300", "ETag": etag}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return JSONResponse(content=jsonable_encoder({"datos": data, "meta": meta}), headers=headers)


def _require_geography(db: Connection, geography_id: str) -> Any:
    row = db.execute(select(geografias).where(geografias.c.id == geography_id)).one_or_none()
    if row is None:
        raise ApiError(404, "geografia_desconocida", "La geografía solicitada no existe.")
    return row


def _require_rubro(db: Connection, rubro_id: str) -> Any:
    row = db.execute(select(rubros).where(rubros.c.id == rubro_id)).one_or_none()
    if row is None:
        raise ApiError(404, "rubro_desconocido", "El rubro solicitado no existe.")
    return row


def _require_series(db: Connection, geography_id: str, rubro_id: str) -> int:
    value = db.scalar(
        select(series.c.id).where(
            and_(series.c.geografia_id == geography_id, series.c.rubro_id == rubro_id)
        )
    )
    if value is None:
        raise ApiError(404, "serie_no_disponible", "La serie solicitada no existe.")
    return value


def _source_max(db: Connection, serie_id: int) -> date | None:
    return db.scalar(
        select(func.max(observaciones.c.periodo)).where(
            observaciones.c.serie_id == serie_id,
            observaciones.c.valor.is_not(None),
        )
    )


def _select_period(value: str | None, source_max: date | None) -> date | None:
    if source_max is None:
        return None
    selected = _parse_month(value) if value else source_max
    if selected > source_max:
        raise ApiError(422, "periodo_futuro", "El periodo solicitado aún no está publicado.")
    return selected


def _history_range(
    desde: str | None, hasta: str | None, source_max: date | None
) -> tuple[date, date]:
    if source_max is None:
        raise ApiError(
            422, "sin_periodo_fuente", "No hay un periodo publicado para esta geografía."
        )
    end = _select_period(hasta, source_max)
    assert end is not None
    start = (
        _parse_month(desde)
        if desde
        else max(date(2018, 1, 1), _add_months(end, 1 - DEFAULT_HISTORY_MONTHS))
    )
    if start > end:
        raise ApiError(422, "rango_invertido", "'desde' no puede ser posterior a 'hasta'.")
    if _month_count(start, end) > MAX_MONTHS:
        raise ApiError(422, "rango_excesivo", f"El rango máximo es de {MAX_MONTHS} meses.")
    return start, end


def _parse_month(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m").date()
    except ValueError as error:
        raise ApiError(
            422, "parametros_invalidos", "El periodo debe usar el formato YYYY-MM."
        ) from error


def _add_months(value: date, months: int) -> date:
    index = value.year * 12 + value.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def _month_count(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month + 1


def _months(start: date, end: date) -> Generator[date, None, None]:
    current = start
    while current <= end:
        yield current
        current = _add_months(current, 1)


def _metrics_at_period(db: Connection, serie_id: int, period: date) -> dict[str, ResultadoMetrica]:
    return {
        measure: next(
            iter(serie_metricas(db, serie_id=serie_id, medida=measure, desde=period, hasta=period)),
            _missing_metric(period, measure),
        )
        for measure in ("indice", "mensual", "anual")
    }


def _missing_metric(period: date, measure: Medida) -> ResultadoMetrica:
    units = {"indice": "puntos_indice", "mensual": "porcentaje", "anual": "porcentaje"}
    return ResultadoMetrica(period, None, "no_publicado", units[measure])


def _measurement(metric: ResultadoMetrica, *, include_period: bool = False) -> dict[str, object]:
    result: dict[str, object] = {
        "valor": _number(metric.valor, metric.unidad),
        "estado": metric.estado,
    }
    if include_period:
        result["periodo"] = _month(metric.periodo)
    else:
        result["unidad"] = metric.unidad
    return result


def _number(value: Decimal | None, unit: str) -> float | None:
    if value is None:
        return None
    if unit == "porcentaje":
        value = value.quantize(_RATE_QUANTUM, rounding=ROUND_HALF_UP)
    return float(value)


def _month(value: date | None) -> str | None:
    return value.strftime("%Y-%m") if value else None


def _geografia(row: Any) -> dict[str, object]:
    return {"id": row.id, "nivel": row.nivel, "nombre": row.nombre}


def _empty_summary() -> dict[str, object]:
    return {
        "periodo": None,
        "indice": {"valor": None, "estado": "no_publicado", "unidad": "puntos_indice"},
        "mensual": {"valor": None, "estado": "no_publicado", "unidad": "porcentaje"},
        "anual": {"valor": None, "estado": "no_publicado", "unidad": "porcentaje"},
    }
