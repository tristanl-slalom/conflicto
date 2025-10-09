"""merge migration heads

Revision ID: f35d7574c2e4
Revises: 16f52f3cf49a, 3edee9ecd4f6
Create Date: 2025-10-08 22:27:01.889558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f35d7574c2e4'
down_revision = ('16f52f3cf49a', '3edee9ecd4f6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
