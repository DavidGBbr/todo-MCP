"""Initial schema: todos and subtasks tables

Revision ID: 001
Revises:
Create Date: 2026-06-17

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "todos",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("priority", sa.String(10), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("project", sa.String(255), nullable=True),
        sa.Column(
            "tags",
            ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column("assignee", sa.String(255), nullable=True),
        sa.Column("effort", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "subtasks",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("todo_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "done", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.ForeignKeyConstraint(["todo_id"], ["todos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_todos_deleted_at", "todos", ["deleted_at"])
    op.create_index("ix_todos_status", "todos", ["status"])
    op.create_index("ix_todos_priority", "todos", ["priority"])
    op.create_index("ix_todos_due_date", "todos", ["due_date"])
    op.create_index("ix_todos_project", "todos", ["project"])
    op.create_index("ix_todos_assignee", "todos", ["assignee"])
    op.create_index("ix_todos_tags", "todos", ["tags"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("ix_todos_tags", table_name="todos", postgresql_using="gin")
    op.drop_index("ix_todos_assignee", table_name="todos")
    op.drop_index("ix_todos_project", table_name="todos")
    op.drop_index("ix_todos_due_date", table_name="todos")
    op.drop_index("ix_todos_priority", table_name="todos")
    op.drop_index("ix_todos_status", table_name="todos")
    op.drop_index("ix_todos_deleted_at", table_name="todos")
    op.drop_table("subtasks")
    op.drop_table("todos")
