import aiohttp
from typing import Any
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Response(BaseModel):
    status_code: int
    body: dict | list | None = None

    def ok(self) -> bool:
        return self.status_code in (200, 201)


class Method:
    GET = 'GET'
    POST = 'POST'
    PATCH = 'PATCH'
    DELETE = 'DELETE'


class Requester:
    def __init__(self, base_url: str):
        self.__base_url = base_url
        self.__base_headers = {
            'Content-Type': 'application/json',
        }

    async def _request(self, method: str, endpoint: str, query: dict[str, Any] = None, body: dict[str, Any] = None) -> Response:
        kwargs = {}

        if query is not None:
            kwargs['params'] = query

        if body is not None:
            kwargs['json'] = body

        kwargs['headers'] = self.__base_headers

        async with aiohttp.ClientSession() as session:
            async with session.request(method=method, url=f"{self.__base_url}/{endpoint}", **kwargs) as response:
                return Response(
                    status_code=response.status,
                    body=await response.json(),
                )

    async def get(self, endpoint: str, query: dict[str, Any] = None) -> Response:
        return await self._request(Method.GET, endpoint, query)

    async def post(self, endpoint: str, query: dict[str, Any] = None, body: dict[str, Any] = None) -> Response:
        return await self._request(Method.POST, endpoint, query, body)

    async def patch(self, endpoint: str, query: dict[str, Any] = None, body: dict[str, Any] = None) -> Response:
        return await self._request(Method.PATCH, endpoint, query, body)

    async def delete(self, endpoint: str, query: dict[str, Any] = None) -> Response:
        return await self._request(Method.DELETE, endpoint, query)
