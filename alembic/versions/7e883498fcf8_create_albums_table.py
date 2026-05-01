"""create albums table

Revision ID: 7e883498fcf8
Revises: 47415f241c1e
Create Date: 2026-05-01 04:26:39.482049
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '7e883498fcf8'
down_revision = '47415f241c1e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "albums",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_albums_id"), "albums", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_albums_id"), table_name="albums")
    op.drop_table("albums")
