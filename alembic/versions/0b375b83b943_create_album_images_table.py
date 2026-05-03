"""create album images table

Revision ID: 0b375b83b943
Revises: 3f302cd9f2d2
Create Date: 2026-05-03 04:32:56.833536
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '0b375b83b943'
down_revision = '3f302cd9f2d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "album_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("album_id", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.Integer(), nullable=False),       
        sa.Column("created_at", sa.DateTime(), nullable=False),

        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["album_id"], ["albums.id"]),        
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        op.f("ix_album_images_id"),
        "album_images",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_album_images_image_id"),
        "album_images",
        ["image_id"],
        unique=False,
    )


    op.create_index(
        op.f("ix_album_images_album_id"),
        "album_images",
        ["album_id"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(op.f("ix_album_images_album_id"), table_name="album_images")
    op.drop_index(op.f("ix_album_images_image_id"), table_name="album_images")
    op.drop_index(op.f("ix_album_images_id"), table_name="album_images")
    op.drop_table("album_images")
