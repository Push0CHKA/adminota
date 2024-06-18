import time
from json import JSONDecodeError
from typing import Literal

import httpx
from loguru import logger
from httpx import TimeoutException, ConnectError, Response

from src.core.schemas.api_schemas import RequestSettings


class Request:
    logger = logger

    @classmethod
    def dispatch_response(cls, resp: Response) -> dict:
        try:
            return resp.json()
        except JSONDecodeError:
            cls.logger.error(
                f"Got not jsonable response with body {resp.text}"
            )

    @classmethod
    async def common_request(
        cls,
        method: Literal["POST", "GET"],
        url: str,
        headers: dict = None,
        data: dict = None,
        params: dict = None,
        json_: dict = None,
    ) -> tuple[int, dict | str]:
        """Common request"""
        before_request_time = time.time()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.request(
                    method,
                    url,
                    headers=headers,
                    follow_redirects=True,
                    data=data,
                    params=params,
                    json=json_,
                    timeout=RequestSettings.timeout,
                )
        except TimeoutException as err:
            cls.logger.warning(
                f"Timeout error on sending request to {url}: {err}"
            )
            raise
        except ConnectError as err:
            cls.logger.warning(
                f"Connection error on sending request to {url}: {err}"
            )
            raise
        except Exception as err:
            cls.logger.error(
                f"Unhandled error when try make request. Error: {err}"
            )
            raise
        finally:
            cls.logger.debug(
                f"Make request to {url}.\n"
                f"headers: {headers}\n"
                f"data: {data}\n"
                f"params: {params}\n"
                f"json: {json_}\n"
                f"request time: {(time.time() - before_request_time) * 1000}\n"
                # f"response body: {resp.text if resp else None}\n"
                f"status code: {resp.status_code if resp else None}"
            )
        resp_data = cls.dispatch_response(resp) if len(resp.text) else ""
        if resp.is_success:
            cls.logger.debug(f"Received success response [{resp.status_code}]")
        else:
            cls.logger.warning(
                f"Received not success response [{resp.status_code}]"
            )
        return resp.status_code, resp_data
