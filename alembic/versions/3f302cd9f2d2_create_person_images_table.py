"""create person images table

Revision ID: 3f302cd9f2d2
Revises: 7e883498fcf8
Create Date: 2026-05-01 08:28:35.657433
"""
from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '3f302cd9f2d2'
down_revision = '7e883498fcf8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "person_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("top", sa.Integer(), nullable=False),
        sa.Column("right", sa.Integer(), nullable=False),
        sa.Column("bottom", sa.Integer(), nullable=False),
        sa.Column("left", sa.Integer(), nullable=False),
        
        sa.Column("created_at", sa.DateTime(), nullable=False),

        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["image_id"], ["images.id"]),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"]),        
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        op.f("ix_person_images_id"),
        "person_images",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_person_images_image_id"),
        "person_images",
        ["image_id"],
        unique=False,
    )


    op.create_index(
        op.f("ix_person_images_person_id"),
        "person_images",
        ["person_id"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(op.f("ix_person_images_person_id"), table_name="person_images")
    op.drop_index(op.f("ix_person_images_image_id"), table_name="person_images")
    op.drop_index(op.f("ix_person_images_id"), table_name="person_images")
    op.drop_table("person_images")
