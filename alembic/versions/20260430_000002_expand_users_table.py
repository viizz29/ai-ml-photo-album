"""Expand users table

Revision ID: 20260430_000002
Revises: 20260430_000001
Create Date: 2026-04-30 00:00:02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260430_000002"
down_revision = "20260430_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "id",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        autoincrement=True,
        existing_nullable=False,
        postgresql_using="id::bigint",
    )
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq AS bigint")
    op.execute("ALTER SEQUENCE users_id_seq OWNED BY users.id")
    op.execute(
        """
        SELECT setval(
            'users_id_seq',
            COALESCE((SELECT MAX(id) FROM users), 1),
            (SELECT COUNT(*) > 0 FROM users)
        )
        """
    )
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')")

    op.add_column("users", sa.Column("name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.execute("UPDATE users SET name = email WHERE name IS NULL")
    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE users SET updated_at = NOW() WHERE updated_at IS NULL")

    op.alter_column("users", "email", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "password", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "name", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "created_at", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("users", "updated_at", existing_type=sa.DateTime(), nullable=False)


def downgrade() -> None:
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "name")

    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS users_id_seq")
    op.alter_column(
        "users",
        "id",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="id::integer",
    )
    op.alter_column("users", "password", existing_type=sa.String(), nullable=True)
    op.alter_column("users", "email", existing_type=sa.String(), nullable=True)
