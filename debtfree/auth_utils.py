"""Utilitários de autenticação — hash de senha sem dependência externa."""
import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    """Gera hash seguro com PBKDF2-SHA256 + salt aleatório."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 260_000)
    return f"pbkdf2:{salt}:{hashed.hex()}"


def check_password(password: str, stored_hash: str) -> bool:
    """Verifica senha contra hash armazenado. Tempo constante para evitar timing attacks."""
    try:
        _, salt, expected = stored_hash.split(":", 2)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 260_000)
        return hmac.compare_digest(actual.hex(), expected)
    except Exception:
        return False
