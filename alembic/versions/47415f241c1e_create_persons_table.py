"""create persons table

Revision ID: 47415f241c1e
Revises: 4c1764602ef8
Create Date: 2026-05-01 04:25:27.066057
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '47415f241c1e'
down_revision = '4c1764602ef8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("encoding", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )


def downgrade() -> None:
    op.drop_table("persons")
