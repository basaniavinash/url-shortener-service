import secrets
import string
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from app import repo
from app.config import ID_LENGTH, BASE_URL
from app.models import ShortUrlRow

_ALPHABET = string.ascii_letters+string.digits

def _new_id(n: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(n))

def _valid_url(url: str) -> bool:
    try:
        u = urlparse(str(url))
        return u.scheme in ("http", "https") and bool(u.netloc)
    except Exception:
        return False

class ShortenerService:
    """Business rules: generate IDs, validate, enforce/active expiry"""

    def create(self, long_url: str, alias: Optional[str], expires_at_iso: Optional[str], owner_id: str):
        if not _valid_url(long_url):
            raise ValueError("Invalid URL")

        code = alias if alias else _new_id(ID_LENGTH)
        if repo.repo_exists(code):
            raise KeyError("Alias already taken")

        expires_at_dt = None
        if expires_at_iso:
            try:
                expires_at_dt = datetime.fromisoformat(expires_at_iso.replace("Z", "+00:00"))
            except Exception:
                raise ValueError("Invalid expires at provided")

        row = ShortUrlRow(
            id = code,
            expires_at=expires_at_dt,
            long_url=str(long_url),
            created_at=datetime.now(timezone.utc),
            is_active=True,
            owner_id=owner_id
        )

        repo.repo_create(row)
        return {"id": code, "short_url": f"{BASE_URL}/{code}"}

    def resolve(self, _id: str) -> str:
        row = repo.repo_get(_id)
        if not row:
            raise LookupError("ID does not exist")
        if not row.is_active:
            raise PermissionError("Inactive")
        if row.expires_at and row.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            raise PermissionError("Expired")
        return str(row.long_url).strip()

    def expand(self, _id: str):
        row = repo.repo_get(_id)
        if not row:
            raise LookupError("ID does not exist")
        return {"id": row.id, "long_url": row.long_url}

    def list_by_owner(self, owner: str):
        rows = repo.repo_list_by_owner(owner)
        return [{"id": row.id, "long_url": row.long_url, "created_at": row.created_at.isoformat()} for row in rows]
