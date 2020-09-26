from typing import Optional

from ecies import decrypt
from ecies import encrypt
from fastapi import FastAPI
from fastapi import Form
from fastapi import HTTPException
from fastapi.responses import Response

app = FastAPI()


def resp_string(msg):
    return Response(content=msg, media_type="plain/text")


@app.post("/")
async def encrypt_decrypt(
    prv: Optional[str] = Form(None),
    pub: Optional[str] = Form(None),
    data: str = Form(...),
):
    if prv and data:
        try:
            decrypted = decrypt(prv, bytes.fromhex(data))
            return resp_string(decrypted)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid private key")
    elif pub and data:
        try:
            encrypted = encrypt(pub, data.encode())
            return resp_string(encrypted.hex())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid public key")
    else:
        raise HTTPException(status_code=400, detail="Invalid request")
