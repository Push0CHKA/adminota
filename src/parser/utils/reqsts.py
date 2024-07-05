import asyncio
from typing import Literal

from httpx import TimeoutException, ConnectError
from loguru import logger

from src.core.utils.reqsts import Request
from src.parser.exceptions import exc


class VkApiRequest(Request):
    logger = logger

    @classmethod
    async def request(
        cls,
        method: Literal["POST", "GET"],
        url: str,
        headers: dict = None,
        data: dict = None,
        params: dict = None,
        json_: dict = None,
        attempts_count: int = 5,
        request_delay: int = 5,
    ):
        for attempt in range(attempts_count):
            cls.logger.debug(f"Try make request to {url}. Attempt {attempt + 1}")
            try:
                code, data = await cls.common_request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    params=params,
                    json_=json_,
                )
            except (TimeoutException, ConnectError):
                continue
            except Exception:
                raise
            finally:
                await asyncio.sleep(request_delay)

            if error := data.get("error", {}):
                raise exc.VkApiError(
                    error_code=error.get("error_code"),
                    message=error.get("error_msg"),
                )

            if 200 <= code < 300 and data.get("response", {}):
                return data["response"]

        cls.logger.error(
            f"Failed receive success response. Attempts count: {attempts_count}"
        )
        raise ConnectError("Failed receive success response")
