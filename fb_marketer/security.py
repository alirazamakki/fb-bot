from __future__ import annotations

from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet


def ensure_fernet_key(key_file: Path) -> None:
    if not key_file.exists():
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        key_file.write_bytes(key)


def load_fernet(key_file: Path) -> Fernet:
    ensure_fernet_key(key_file)
    key = key_file.read_bytes()
    return Fernet(key)


def encrypt_text(plaintext: str, fernet: Fernet) -> str:
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_text(ciphertext: str, fernet: Fernet) -> str:
    return fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")

