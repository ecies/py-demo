from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import AsyncTestClient


async def test_encrypt(client: AsyncTestClient):
    response = await client.post(
        "/",
        data={
            "data": "abc",
            "pub": "0x98afe4f150642cd05cc9d2fa36458ce0a58567daeaf5fde7333ba9b403011140a4e28911fcf83ab1f457a30b4959efc4b9306f514a4c3711a16a80e3b47eb58b",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == HTTP_201_CREATED
