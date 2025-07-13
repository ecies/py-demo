from typing import Optional

from ecies import decrypt, encrypt
from ecies.config import Config, EllipticCurve
from litestar import Litestar, MediaType, Request, Response, post
from litestar.enums import RequestEncodingType
from litestar.openapi import OpenAPIConfig
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.params import Body
from litestar.status_codes import HTTP_400_BAD_REQUEST
from msgspec import Struct


# request and response
class Payload(Struct):
    data: str
    prv: Optional[str] = None
    pub: Optional[str] = None
    curve: EllipticCurve = "secp256k1"


class RequestError(Struct):
    detail: str


# exceptions
class RequestException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


# exception handlers
def request_exception_handler(_: Request, exc: RequestException) -> Response:
    return Response(
        media_type=MediaType.JSON,
        content={"detail": exc.detail},
        status_code=HTTP_400_BAD_REQUEST,
    )


# utils
def make_readable(data: bytes):
    try:
        return data.decode()
    except ValueError:
        return data.hex()


# routes
@post(
    "/",
    responses={
        HTTP_400_BAD_REQUEST: ResponseSpec(data_container=RequestError),
    },
)
async def encrypt_decrypt(
    data: Payload = Body(media_type=RequestEncodingType.URL_ENCODED),
) -> str:
    config = Config(elliptic_curve=data.curve)
    if data.prv and data.data:
        try:
            decrypted = decrypt(data.prv, bytes.fromhex(data.data), config)
            return make_readable(decrypted)
        except ValueError:
            raise RequestException(detail="Invalid private key or data")
    elif data.pub and data:
        try:
            encrypted = encrypt(data.pub, data.data.encode(), config)
            return encrypted.hex()
        except ValueError:
            raise RequestException(detail="Invalid public key or data")
    else:
        raise RequestException(detail="Invalid request")


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
