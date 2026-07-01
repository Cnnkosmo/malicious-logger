from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    urls: Mapped[list[Url]] = relationship(back_populates="source")
    ip_addresses: Mapped[list[IpAddress]] = relationship(back_populates="source")


class Url(Base):
    __tablename__ = "urls"
    __table_args__ = (UniqueConstraint("url", "source_id", name="uq_url_source"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    host: Mapped[str | None] = mapped_column(String(255), index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # URLHaus-specific — null for OpenPhish rows
    urlhaus_id: Mapped[int | None] = mapped_column(Integer)
    url_status: Mapped[str | None] = mapped_column(String(10))
    last_online: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    threat: Mapped[str | None] = mapped_column(String(100))
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    urlhaus_link: Mapped[str | None] = mapped_column(Text)
    reporter: Mapped[str | None] = mapped_column(String(100))

    source: Mapped[Source] = relationship(back_populates="urls")


class IpAddress(Base):
    __tablename__ = "ip_addresses"
    __table_args__ = (UniqueConstraint("address", "source_id", name="uq_ip_source"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    address: Mapped[str] = mapped_column(INET, nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # AlienVault fields
    reliability: Mapped[int] = mapped_column(SmallInteger)
    risk: Mapped[int] = mapped_column(SmallInteger)
    threat_type: Mapped[str] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(2))
    city: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]

    source: Mapped[Source] = relationship(back_populates="ip_addresses")
