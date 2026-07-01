"""initial schema

Revision ID: 03cd2a69bb48
Revises: 
Create Date: 2026-07-01 21:39:54.697666

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, INET

revision: str = '03cd2a69bb48'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "urls",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("host", sa.String(255), nullable=True),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        # URLHaus-specific — null for OpenPhish rows
        sa.Column("urlhaus_id", sa.Integer, nullable=True),
        sa.Column("url_status", sa.String(10), nullable=True),
        sa.Column("last_online", sa.DateTime(timezone=True), nullable=True),
        sa.Column("threat", sa.String(100), nullable=True),
        sa.Column("tags", ARRAY(sa.Text), nullable=True),
        sa.Column("urlhaus_link", sa.Text, nullable=True),
        sa.Column("reporter", sa.String(100), nullable=True),
        sa.UniqueConstraint("url", "source_id", name="uq_url_source"),
    )
    op.create_index("ix_urls_url", "urls", ["url"])
    op.create_index("ix_urls_host", "urls", ["host"])

    op.create_table(
        "ip_addresses",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("address", INET, nullable=False),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reliability", sa.SmallInteger, nullable=False),
        sa.Column("risk", sa.SmallInteger, nullable=False),
        sa.Column("threat_type", sa.String(100), nullable=False),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Double, nullable=True),
        sa.Column("longitude", sa.Double, nullable=True),
        sa.UniqueConstraint("address", "source_id", name="uq_ip_source"),
    )
    op.create_index("ix_ip_addresses_address", "ip_addresses", ["address"])


def downgrade() -> None:
    op.drop_table("ip_addresses")
    op.drop_table("urls")
    op.drop_table("sources")
