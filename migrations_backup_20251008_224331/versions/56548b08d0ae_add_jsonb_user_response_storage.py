"""Add JSONB user response storage

Revision ID: 56548b08d0ae
Revises: a663bb0881d7
Create Date: 2025-10-07 14:11:43.452941

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "56548b08d0ae"
down_revision = "a663bb0881d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if enum already exists and create it if it doesn't
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'new_activity_status'")
    ).fetchone()

    if not result:
        # Create new_activity_status enum (different from existing activity_status)
        new_activity_status = postgresql.ENUM(
            "draft", "active", "completed", "cancelled", name="new_activity_status"
        )
        new_activity_status.create(connection)

    # Get the enum type for use in table definition
    new_activity_status_type = postgresql.ENUM(
        "draft",
        "active",
        "completed",
        "cancelled",
        name="new_activity_status",
        create_type=False,
    )

    # Create new_activities table (renamed to avoid conflicts)
    op.create_table(
        "new_activities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column(
            "status", new_activity_status_type, nullable=False, server_default="draft"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create user_responses table
    op.create_table(
        "user_responses",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column(
            "response_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["new_activities.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"], ["participants.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for optimal performance
    op.create_index(
        "idx_new_activities_session_order",
        "new_activities",
        ["session_id", "order_index"],
    )
    op.create_index("idx_new_activities_status", "new_activities", ["status"])
    op.create_index("idx_new_activities_type", "new_activities", ["type"])
    op.create_index(
        "idx_new_activities_config_gin",
        "new_activities",
        ["config"],
        postgresql_using="gin",
    )

    op.create_index(
        "idx_user_responses_session_activity",
        "user_responses",
        ["session_id", "activity_id"],
    )
    op.create_index("idx_user_responses_created_at", "user_responses", ["created_at"])
    op.create_index(
        "idx_user_responses_participant", "user_responses", ["participant_id"]
    )
    op.create_index(
        "idx_user_responses_data_gin",
        "user_responses",
        ["response_data"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_user_responses_data_gin", table_name="user_responses")
    op.drop_index("idx_user_responses_participant", table_name="user_responses")
    op.drop_index("idx_user_responses_created_at", table_name="user_responses")
    op.drop_index("idx_user_responses_session_activity", table_name="user_responses")

    op.drop_index("idx_new_activities_config_gin", table_name="new_activities")
    op.drop_index("idx_new_activities_type", table_name="new_activities")
    op.drop_index("idx_new_activities_status", table_name="new_activities")
    op.drop_index("idx_new_activities_session_order", table_name="new_activities")

    # Drop tables
    op.drop_table("user_responses")
    op.drop_table("new_activities")

    # Drop enum
    try:
        new_activity_status = postgresql.ENUM(
            "draft", "active", "completed", "cancelled", name="new_activity_status"
        )
        new_activity_status.drop(op.get_bind(), checkfirst=True)
    except Exception as e:
        # If enum doesn't exist, that's fine
        if "does not exist" in str(e):
            pass
        else:
            raise e
