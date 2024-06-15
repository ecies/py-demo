from typing import Optional

from ecies import decrypt, encrypt
from fastapi import FastAPI, Form, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Error(BaseModel):
    detail: str


@app.post("/", responses={400: {"model": Error}})
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
            return resp_error("Invalid private key or data")
    elif pub and data:
        try:
            encrypted = encrypt(pub, data.encode())
            return resp_string(encrypted.hex())
        except ValueError:
            return resp_error("Invalid public key or data")
    else:
        return resp_error("Invalid request")


def resp_string(msg):
    return Response(content=msg, media_type="plain/text")


def resp_error(msg):
    return JSONResponse(content={"detail": msg}, status_code=400)
