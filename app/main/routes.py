from flask import request, abort
from ecies import encrypt, decrypt

from app.main import bp


@bp.route("/", methods=["POST"])
def index():
    prv = request.form.get("prv", "")
    pub = request.form.get("pub", "")
    data = request.form.get("data", "")
    if prv and data:
        decrypted = decrypt(prv, bytes.fromhex(data))
        return decrypted
    elif pub and data:
        encrypted = encrypt(pub, data.encode())
        return encrypted.hex()
    else:
        abort(400)
