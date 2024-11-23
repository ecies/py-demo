from typing import Optional

from ecies import decrypt, encrypt
from litestar import Litestar, MediaType, Request, Response, post
from litestar.enums import RequestEncodingType
from litestar.openapi import OpenAPIConfig
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.params import Body
from msgspec import Struct


class RequestException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class Payload(Struct):
    data: str
    prv: Optional[str] = None
    pub: Optional[str] = None


class RequestError(Struct):
    detail: str


@post(
    "/",
    responses={
        400: ResponseSpec(data_container=RequestError),
    },
)
async def encrypt_decrypt(
    data: Payload = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> str:
    if data.prv and data.data:
        try:
            decrypted = decrypt(data.prv, bytes.fromhex(data.data))
            try:
                return decrypted.decode()
            except ValueError:
                return decrypted.hex()
        except ValueError:
            raise RequestException(detail="Invalid private key or data")
    elif data.pub and data:
        try:
            encrypted = encrypt(data.pub, data.data.encode())
            return encrypted.hex()
        except ValueError:
            raise RequestException(detail="Invalid public key or data")
    else:
        raise RequestException(detail="Invalid request")


def request_exception_handler(_: Request, exc: RequestException) -> Response:
    return Response(
        media_type=MediaType.JSON,
        content={"detail": exc.detail},
        status_code=400,
    )


app = Litestar(
    route_handlers=[encrypt_decrypt],
    exception_handlers={RequestException: request_exception_handler},
    openapi_config=OpenAPIConfig(
        "eciespy demo",
        version="0.1.0",
        path="/docs",
        render_plugins=[SwaggerRenderPlugin()],
    ),
)
