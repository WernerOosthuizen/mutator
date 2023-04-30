"""table structure

Revision ID: 09b34a6c797a
Revises:

"""
from alembic import op
from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, ForeignKey, Boolean

# revision identifiers, used by Alembic.

revision = "09b34a6c797a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "test_run",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("endpoint", JSON),
        Column("config", JSON),
        Column("batch_id", String(45)),
        Column("state", String(45)),
        Column("state_description", String(255)),
        Column("passed", Boolean),
        Column("test_generated_count", Integer),
        Column("test_result_count", Integer),
        Column("owner", String(255)),
        Column("run_attempts", Integer),
        Column("analysis_attempts", Integer),
        Column("lock_start_date", TIMESTAMP),
        Column("lock_end_date", TIMESTAMP),
        Column("create_date", TIMESTAMP),
        Column("last_update_date", TIMESTAMP),
        Column("version", Integer, nullable=False),
    )

    op.create_table(
        "test_result",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("test_run_id", Integer, ForeignKey("test_run.id", ondelete="CASCADE")),
        Column("test_value", String(10000)),
        Column("test_type", String(255)),
        Column("passed", Boolean),
        Column("request_hash", String(255)),
        Column("request_method", String(45)),
        Column("request_headers", JSON),
        Column("request_url", String(10000)),
        Column("request_body", JSON),
        Column("response_hash", String(255)),
        Column("response_headers", JSON),
        Column("response_body", JSON),
        Column("response_status_code", Integer),
        Column("create_date", TIMESTAMP),
    )

    op.create_index("idx_test_result_test_run_id", "test_result", ["test_run_id"])
    op.create_index("idx_test_result_request_hash", "test_result", ["request_hash"])

    op.create_table(
        "validation",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("type", String(255)),
        Column("passed", Boolean),
        Column("message", String(255)),
        Column(
            "test_result_id", Integer, ForeignKey("test_result.id", ondelete="CASCADE")
        ),
        Column("create_date", TIMESTAMP),
    )

    op.create_index("idx_validation_test_result_id", "validation", ["test_result_id"])

    op.create_table(
        "test_queue",
        Column(
            "id", String(45)
        ),  # UUID in case of duplicate test_run_id + test_hash combinations
        Column("test_run_id", Integer),
        Column("test_hash", String(255)),
        Column("test", JSON),
        Column("create_date", TIMESTAMP),
    )

    op.create_index(
        "idx_test_queue_test_run_id_test_hash",
        "test_queue",
        ["id", "test_run_id", "test_hash"],
    )
    op.create_index("idx_test_queue_create_date", "test_queue", ["create_date"])


def downgrade():
    op.drop_table("test_run")
    op.drop_table("test_result")
    op.drop_table("validation")
    op.drop_table("test_queue")
