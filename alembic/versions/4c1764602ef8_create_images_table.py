"""create images table

Revision ID: 4c1764602ef8
Revises: 6a3a5cc8b068
Create Date: 2026-05-01 04:24:48.939950
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '4c1764602ef8'
down_revision = '6a3a5cc8b068'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("stored_path", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("commentary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("stored_path"),
    )
    op.create_index(op.f("ix_images_id"), "images", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_images_id"), table_name="images")
    op.drop_table("images")
