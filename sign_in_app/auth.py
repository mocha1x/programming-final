import hashlib


def hash_password(password: str) -> str:
    """Return a SHA-256 hex digest of the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Return True if plain_password hashes to stored_hash."""
    return hash_password(plain_password) == stored_hash
