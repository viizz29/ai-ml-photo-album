"""Initial schema

Revision ID: 20260430_000001
Revises:
Create Date: 2026-04-30 00:00:01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260430_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "face_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("stored_path", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(op.f("ix_face_images_id"), "face_images", ["id"], unique=False)
    op.create_unique_constraint(
        "uq_face_images_stored_path", "face_images", ["stored_path"]
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "recognized_faces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("person_id", sa.String(), nullable=False),
        sa.Column("encoding", sa.Text(), nullable=False),
        sa.Column("top", sa.Integer(), nullable=False),
        sa.Column("right", sa.Integer(), nullable=False),
        sa.Column("bottom", sa.Integer(), nullable=False),
        sa.Column("left", sa.Integer(), nullable=False),
        sa.Column("matched_face_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["image_id"], ["face_images.id"]),
        sa.ForeignKeyConstraint(["matched_face_id"], ["recognized_faces.id"]),
    )
    op.create_index(
        op.f("ix_recognized_faces_id"), "recognized_faces", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_recognized_faces_image_id"),
        "recognized_faces",
        ["image_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recognized_faces_person_id"),
        "recognized_faces",
        ["person_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_recognized_faces_person_id"), table_name="recognized_faces")
    op.drop_index(op.f("ix_recognized_faces_image_id"), table_name="recognized_faces")
    op.drop_index(op.f("ix_recognized_faces_id"), table_name="recognized_faces")
    op.drop_table("recognized_faces")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_constraint("uq_face_images_stored_path", "face_images", type_="unique")
    op.drop_index(op.f("ix_face_images_id"), table_name="face_images")
    op.drop_table("face_images")
