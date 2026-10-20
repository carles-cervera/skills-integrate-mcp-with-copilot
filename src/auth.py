import hashlib
import hmac
import json
import secrets
from pathlib import Path

from fastapi import HTTPException, Request


TEACHERS_FILE = Path(__file__).with_name("teachers.json")
PASSWORD_ITERATIONS = 310_000


def load_teacher_store():
    with TEACHERS_FILE.open(encoding="utf-8") as file:
        store = json.load(file)
    if not isinstance(store, dict) or not isinstance(store.get("teachers"), dict):
        raise ValueError("teachers.json must contain a teachers object")
    return store


def teacher_exists(username: str) -> bool:
    return username in load_teacher_store()["teachers"]


def create_password_record(password: str) -> dict[str, str]:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return {"salt": salt.hex(), "password_hash": password_hash.hex()}


def verify_teacher(username: str, password: str) -> bool:
    store = load_teacher_store()
    record = store["teachers"].get(username)
    if not isinstance(record, dict):
        salt = b"mergington-dummy-salt"
        expected_hash = hashlib.pbkdf2_hmac(
            "sha256", b"invalid-user", salt, PASSWORD_ITERATIONS
        )
        supplied_hash = hashlib.pbkdf2_hmac(
            "sha256", (password or "").encode("utf-8"), salt, PASSWORD_ITERATIONS
        )
        hmac.compare_digest(supplied_hash, expected_hash)
        return False

    salt = bytes.fromhex(record["salt"])
    expected_hash = bytes.fromhex(record["password_hash"])
    iterations = int(store.get("iterations", PASSWORD_ITERATIONS))
    supplied_hash = hashlib.pbkdf2_hmac(
        "sha256", (password or "").encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(supplied_hash, expected_hash)


def require_teacher(request: Request) -> str:
    username = request.session.get("teacher")
    if not isinstance(username, str) or not teacher_exists(username):
        request.session.clear()
        raise HTTPException(status_code=401, detail="Teacher login required")
    return username