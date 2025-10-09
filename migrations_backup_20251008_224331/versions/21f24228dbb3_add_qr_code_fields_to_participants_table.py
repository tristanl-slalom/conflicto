"""Add QR code fields to participants table

Revision ID: 21f24228dbb3
Revises: 7b81da24b89f
Create Date: 2025-10-08 13:49:04.580225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "21f24228dbb3"
down_revision = "7b81da24b89f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to participants table for QR code onboarding
    op.add_column(
        "participants", sa.Column("nickname", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "participants",
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "participants",
        sa.Column("connection_data", sa.JSON(), nullable=True, default={}),
    )

    # Update existing participants to have a default nickname based on display_name
    op.execute(
        "UPDATE participants SET nickname = COALESCE(display_name, 'User' || id::text) WHERE nickname IS NULL"
    )

    # Now make nickname NOT NULL
    op.alter_column("participants", "nickname", nullable=False)

    # Add unique constraint on session_id + nickname
    op.create_unique_constraint(
        "unique_session_nickname", "participants", ["session_id", "nickname"]
    )


def downgrade() -> None:
    # Remove the unique constraint
    op.drop_constraint("unique_session_nickname", "participants", type_="unique")

    # Remove the added columns
    op.drop_column("participants", "connection_data")
    op.drop_column("participants", "last_seen")
    op.drop_column("participants", "nickname")
