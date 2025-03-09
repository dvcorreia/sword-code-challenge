from __future__ import annotations

from http import HTTPStatus
from typing import Any, Mapping

import structlog
from hypercorn.config import Config
from hypercorn.logging import Logger as HypercornLogger
from hypercorn.typing import ResponseSummary, WWWScope


class Logger(HypercornLogger):
    def __init__(self, _: Config) -> None:
        self._log: structlog.stdlib.BoundLogger = structlog.get_logger()

    async def access(
        self, request: WWWScope, response: ResponseSummary, request_time: float
    ) -> None:
        atoms = self.atoms(request, response, request_time)

        self._log.info(
            event=f"{atoms['method']} {atoms['uri']}",
            **atoms,
        )

    async def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.critical(message, *args, **kwargs)

    async def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.error(message, *args, **kwargs)

    async def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.warning(message, *args, **kwargs)

    async def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.info(message, *args, **kwargs)

    async def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.debug(message, *args, **kwargs)

    async def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.exception(message, *args, **kwargs)

    async def log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        self._log.log(level, message, *args, **kwargs)

    def atoms(
        self,
        request: WWWScope,
        response: ResponseSummary | None,
        request_time: float,
    ) -> Mapping[str, str]:
        """Create and return an access log atoms dictionary.

        This can be overidden and customised if desired. It should
        return a mapping between an access log format key and a value.
        """
        return AccessLogAtoms(request, response, request_time)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.error_logger, name)


class AccessLogAtoms(dict):
    _request_headers = ["user-agent"]

    _response_headers = ["content-length"]

    def __init__(
        self, request: WWWScope, response: ResponseSummary | None, request_time: float
    ) -> None:
        for name, value in request["headers"]:
            n = name.decode("latin1").lower()
            if n in self._request_headers:
                self[n] = value.decode("latin1")

        protocol = request.get("type", "?")
        protocol_version = request.get("http_version", "?")

        client = request.get("client")
        if client is None:
            remote_addr = None
        elif len(client) == 2:
            remote_addr = f"{client[0]}:{client[1]}"
        elif len(client) == 1:
            remote_addr = client[0]
        else:  # make sure not to throw UnboundLocalError
            remote_addr = f"<???{client}???>"
        if request["type"] == "http":
            method = request["method"]
        else:
            method = "GET"

        query_string = request["query_string"].decode()
        path_with_qs = request["path"] + ("?" + query_string if query_string else "")

        status_code = "???"
        if response is not None:
            status_code = response["status"]

        try:
            status_phrase = HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = f"<???{status_code}???>"

        self.update(
            {
                "latency_ms": f"{(request_time * 1_000):.6f}",
                "protocol": protocol + protocol_version,
                "remote_addr": remote_addr,
                "method": method,
                "uri": path_with_qs,
                "status": status_code,
                "status_label": status_phrase,
            }
        )

    def __getitem__(self, key: str) -> str:
        try:
            if key.startswith("{"):
                return super().__getitem__(key.lower())
            else:
                return super().__getitem__(key)
        except KeyError:
            return "-"
