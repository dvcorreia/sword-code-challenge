from __future__ import annotations

import httpx

from clinical_recommendations.platform.healthcheck.protocol import IHealther
from clinical_recommendations.platform.healthcheck.types import Healthcheck


class OPAHealthcheck(IHealther):
    def __init__(
        self,
        opa_url: str,
        *,
        check_bundles: bool = False,
        check_plugins: bool = False,
        exclude_plugins: list[str] | None = None,
        timeout: float = 2.0,
    ):
        self.url = opa_url.rstrip("/")
        self.check_bundles = check_bundles
        self.check_plugins = check_plugins
        self.exclude_plugins = exclude_plugins or []
        self.timeout = timeout

    def _request_params(self) -> dict[str, str]:
        params = {}

        if self.check_bundles:
            params["bundles"] = "true"

        if self.check_plugins:
            params["plugins"] = "true"

        if len(self.exclude_plugins) > 0:
            params["exclude-plugin"] = self.exclude_plugins

        return params

    async def is_online(self) -> Healthcheck | None:
        health_endpoint = f"{self.url}/health"
        params = self._request_params()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    health_endpoint, params=params, timeout=self.timeout
                )
            except httpx.NetworkError as e:
                return Healthcheck(
                    message="Network error connecting to OPA service",
                    error=self._format_error(e),
                )
            except Exception as e:
                return Healthcheck(
                    message="Unexpected error checking OPA health",
                    error=self._format_error(e),
                )

        if response.status_code == 200:
            return None

        if response.status_code == 500:
            try:
                error_data = response.json()
                error_message = error_data.get("error", "Unknown OPA error")
            except Exception:
                error_message = "OPA service returned unhealthy status"

            return Healthcheck(
                message=error_message,
                error={
                    "opa_health": {
                        "status_code": response.status_code,
                        "response": response.text,
                    }
                },
            )

        return Healthcheck(
            message="Unexpected response from OPA health endpoint",
            error={
                "http_request": {
                    "status_code": response.status_code,
                    "content": response.text,
                    "url": self.url,
                }
            },
        )

    @staticmethod
    def _format_error(exception: Exception) -> dict[str, str]:
        return {"type": type(exception).__name__, "message": str(exception)}

    async def ready(self) -> Healthcheck | None:
        original_bundle_setting = self.check_bundles
        self.check_bundles = True
        result = await self.is_online()
        self.check_bundles = original_bundle_setting
        return result

    async def live(self) -> Healthcheck | None:
        return await self.is_online()
