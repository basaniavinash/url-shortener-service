from datetime import datetime
from typing import Optional

from pydantic import BaseModel, AnyUrl
from sqlalchemy import String, Text, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class ShortUrlRow(Base):
    __tablename__ = "short_url"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    long_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)

class CreateReq(BaseModel):
    url: AnyUrl
    alias: Optional[str] = None
    expires_at: str
    owner_id: str

class CreateResp(BaseModel):
    id: str
    short_url: str

class ExpandResp(BaseModel):
    id: str
    long_url: AnyUrl