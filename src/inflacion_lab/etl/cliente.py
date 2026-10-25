"""Transporte síncrono, acotado y reutilizable para el exportador del INPC."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from time import sleep

import httpx

from ..catalogo import Geografia

DEFAULT_EXPORT_URL = "https://www.inegi.org.mx/app/indicesdepreciosv2/Exportacion.aspx"
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class TransportError(RuntimeError):
    """Indica que el exportador no entregó un CSV válido."""


class InpcClient:
    """Descarga una exportación agrupada, sin interpretar sus datos."""

    def __init__(
        self,
        export_url: str = DEFAULT_EXPORT_URL,
        *,
        client: httpx.Client | None = None,
        attempts: int = 3,
        pause_seconds: float = 0.25,
        sleep_fn: Callable[[float], None] = sleep,
    ) -> None:
        if attempts < 1:
            raise ValueError("attempts debe ser al menos 1.")
        self.export_url = export_url
        self.client = client or httpx.Client(
            timeout=httpx.Timeout(connect=10.0, read=45.0, write=10.0, pool=10.0)
        )
        self._owns_client = client is None
        self.attempts = attempts
        self.pause_seconds = pause_seconds
        self.sleep = sleep_fn

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> InpcClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch(self, geografia: Geografia, start_year: int, end_year: int) -> bytes:
        """Obtiene una sola exportación para sus nueve series explícitas."""
        if start_year > end_year:
            raise ValueError("El año inicial no puede ser posterior al final.")
        params = self._params(geografia, start_year, end_year)
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                response = self.client.get(self.export_url, params=params)
                if response.status_code in RETRYABLE_STATUS:
                    last_error = TransportError(
                        f"{geografia.id}: HTTP {response.status_code} del exportador."
                    )
                    if attempt < self.attempts:
                        self.sleep(self._retry_delay(response))
                        continue
                    raise last_error
                response.raise_for_status()
                self._validate_csv(response, geografia)
                return response.content
            except httpx.RequestError as error:
                last_error = TransportError(f"{geografia.id}: error de red: {error}.")
                if attempt < self.attempts:
                    self.sleep(self.pause_seconds)
                    continue
                raise last_error from error
            except httpx.HTTPStatusError as error:
                raise TransportError(
                    f"{geografia.id}: HTTP {error.response.status_code} del exportador."
                ) from error
        raise TransportError(f"{geografia.id}: descarga fallida: {last_error}")

    @staticmethod
    def _params(geografia: Geografia, start_year: int, end_year: int) -> dict[str, str]:
        return {
            "idEstructura": geografia.id_estructura,
            "ids": ",".join(serie.id_serie_inegi for serie in geografia.series),
            "inicio": str(start_year),
            "fin": str(end_year),
            "_formato": "CSV",
            "_meta": "1",
            "_tipo": "Niveles",
            "_info": "Índices",
            "_orient": "vertical",
        }

    def _retry_delay(self, response: httpx.Response) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after is None:
            return self.pause_seconds
        try:
            return min(float(retry_after), 30.0)
        except ValueError:
            try:
                then = datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S %Z").replace(
                    tzinfo=UTC
                )
            except ValueError:
                return self.pause_seconds
            return min(max((then - datetime.now(UTC)).total_seconds(), 0.0), 30.0)

    @staticmethod
    def _validate_csv(response: httpx.Response, geografia: Geografia) -> None:
        content_type = response.headers.get("Content-Type", "").lower()
        start = response.content.lstrip().lower()
        if (
            not response.content
            or "html" in content_type
            or start.startswith((b"<html", b"<!doctype"))
        ):
            raise TransportError(f"{geografia.id}: la respuesta no es un CSV del INPC.")

    def manifest_parameters(
        self, geografia: Geografia, start_year: int, end_year: int
    ) -> dict[str, str]:
        """Devuelve parámetros seguros para el manifiesto, sin URL ni credenciales."""
        return self._params(geografia, start_year, end_year)

    def pause_between_locations(self) -> None:
        """Respeta la pausa configurada antes de solicitar otra ubicación."""
        self.sleep(self.pause_seconds)
