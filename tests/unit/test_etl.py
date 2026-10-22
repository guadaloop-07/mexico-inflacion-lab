from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

from inflacion_lab.catalogo import Geografia, load_catalog
from inflacion_lab.etl.cliente import InpcClient, TransportError
from inflacion_lab.etl.ejecucion import FetchRunError, fetch_catalog
from inflacion_lab.etl.parser import ParseError, parse_csv

FIXTURES = Path("tests/fixtures/inegi")


@pytest.fixture
def mexico() -> Geografia:
    return load_catalog().geografias[0]


@pytest.mark.parametrize(
    ("filename", "geography_index", "first_series", "first_rubro"),
    [
        ("mexico-2024-2026.csv", 0, "865586", "general"),
        ("jalisco-2024-2026.csv", 14, "900540", "general"),
        ("guadalajara-2024-2026.csv", 53, "879688", "general"),
    ],
)
def test_parser_converts_real_fixture_with_decimal_dates_and_rubros(
    filename: str, geography_index: int, first_series: str, first_rubro: str
) -> None:
    geography = load_catalog().geografias[geography_index]
    observations = parse_csv((FIXTURES / filename).read_bytes(), geography)

    assert len(observations) == 33 * 9
    assert observations[0].serie_id == first_series
    assert observations[0].rubro_id == first_rubro
    assert observations[0].periodo == date(2024, 1, 1)
    assert isinstance(observations[0].valor, Decimal)


def test_parser_accepts_reordered_columns(mexico: Geografia) -> None:
    rows = (FIXTURES / "mexico-2024-2026.csv").read_text(encoding="iso-8859-1").splitlines()
    header = next(index for index, row in enumerate(rows) if row.startswith('"Fecha"'))
    for index in range(header, len(rows)):
        fields = rows[index].split(",")
        rows[index] = ",".join([fields[0], *reversed(fields[1:])])

    observations = parse_csv("\n".join(rows).encode("iso-8859-1"), mexico)

    assert observations[0].serie_id == "866034"
    assert observations[0].rubro_id == "otros_servicios"


@pytest.mark.parametrize("case", ["duplicate", "unknown", "non_numeric", "invalid_date"])
def test_parser_rejects_invalid_csv(mexico: Geografia, case: str) -> None:
    payload = (FIXTURES / "mexico-2024-2026.csv").read_bytes()
    if case == "duplicate":
        payload = payload.replace(b'"865587"', b'"865586"', 1)
        message = "duplicadas"
    elif case == "unknown":
        payload = payload.replace(b'"865587"', b'"desconocida"', 1)
        message = "desconocidas"
    elif case == "non_numeric":
        payload = payload.replace(b'"133.555000000000"', b'"x"', 1)
        message = "no numérico"
    else:
        payload = payload.replace(b'"Ene 2024"', b'"Foo 2024"', 1)
        message = "periodo desconocido"
    with pytest.raises(ParseError, match=message):
        parse_csv(payload, mexico)


def test_parser_rejects_duplicate_observation_key(mexico: Geografia) -> None:
    lines = (FIXTURES / "mexico-2024-2026.csv").read_bytes().splitlines()
    header = next(index for index, line in enumerate(lines) if line.startswith(b'"Fecha"'))
    payload = b"\n".join([*lines, lines[header + 1]])

    with pytest.raises(ParseError, match="clave de observación duplicada"):
        parse_csv(payload, mexico)


def test_client_retries_timeout_and_429_then_returns_csv(mexico: Geografia) -> None:
    payload = (FIXTURES / "mexico-2024-2026.csv").read_bytes()
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ReadTimeout("late", request=request)
        if calls == 2:
            return httpx.Response(429, headers={"Retry-After": "0"}, request=request)
        return httpx.Response(200, content=payload, request=request)

    pauses: list[float] = []
    client = InpcClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)), sleep_fn=pauses.append
    )
    assert client.fetch(mexico, 2018, 2026) == payload
    assert calls == 3
    assert pauses == [0.25, 0.0]


def test_client_rejects_persistent_error_and_html(mexico: Geografia) -> None:
    failed = InpcClient(
        client=httpx.Client(
            transport=httpx.MockTransport(lambda request: httpx.Response(500, request=request))
        ),
        sleep_fn=lambda _: None,
    )
    with pytest.raises(TransportError, match="HTTP 500"):
        failed.fetch(mexico, 2018, 2026)

    html = InpcClient(
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=b"<html>error</html>", request=request)
            )
        )
    )
    with pytest.raises(TransportError, match="no es un CSV"):
        html.fetch(mexico, 2018, 2026)


def test_fetch_preserves_manifest_and_fails_for_incomplete_catalog(
    tmp_path: Path, mexico: Geografia
) -> None:
    catalog = load_catalog()
    payload = (FIXTURES / "mexico-2024-2026.csv").read_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params["idEstructura"] == mexico.id_estructura:
            return httpx.Response(200, content=payload, request=request)
        return httpx.Response(503, request=request)

    client = InpcClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)), sleep_fn=lambda _: None
    )
    with pytest.raises(FetchRunError, match="87 de 88"):
        fetch_catalog(catalog, data_dir=tmp_path, end_year=2026, client=client)

    manifests = list((tmp_path / "raw").glob("*/manifest.json"))
    assert len(manifests) == 1
    assert '"estado": "fallido"' in manifests[0].read_text(encoding="utf-8")
