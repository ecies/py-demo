import pytest
from ecies.config import EllipticCurve
from litestar.status_codes import HTTP_201_CREATED
from litestar.testing import AsyncTestClient


@pytest.fixture(scope="session")
def headers():
    return {"Content-Type": "application/x-www-form-urlencoded"}


@pytest.fixture(scope="session")
def data():
    return "abc🔒"


@pytest.mark.parametrize("curve", [None, "secp256k1", "x25519", "ed25519"])
async def test_encrypt(
    client: AsyncTestClient, data, headers, curve: EllipticCurve | None
):
    if curve is None or curve == "secp256k1":
        sk = "0x95d3c5e483e9b1d4f5fc8e79b2deaf51362980de62dbb082a9a4257eef653d7d"
        pk = "0x98afe4f150642cd05cc9d2fa36458ce0a58567daeaf5fde7333ba9b403011140a4e28911fcf83ab1f457a30b4959efc4b9306f514a4c3711a16a80e3b47eb58b"
    elif curve == "x25519":
        sk = "0xddcfbccd11922e02d1afe6df9f79094d70aba9f7ee7b016fb2cf442f5ab4d2ed"
        pk = "0x787e070a279b5a04df0b0388ec8dea22497505afa0f7453768ff56ba104c6126"
    elif curve == "ed25519":
        sk = "0xa8796a9360b6fac856a9b949066455c2233f5e8b628412c507633762acb94f93"
        pk = "0x3b1c46d8b01e25d66d1484a87fcc49acf148e15e3f25bc2e65eda81dcdac3a19"
    else:
        raise NotImplementedError

    encrypt_data = {"data": data, "pub": pk}
    if curve:
        encrypt_data["curve"] = curve

    response = await client.post("/", data=encrypt_data, headers=headers)
    assert response.status_code == HTTP_201_CREATED

    decrypt_data = {"data": response.text, "prv": sk}
    if curve:
        decrypt_data["curve"] = curve

    response = await client.post("/", data=decrypt_data, headers=headers)
    assert response.text == data
    assert response.status_code == HTTP_201_CREATED
