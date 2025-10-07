"""Rename new_activities table to activities

Revision ID: 7b81da24b89f
Revises: 56548b08d0ae
Create Date: 2025-10-07 16:00:22.904422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b81da24b89f'
down_revision = '56548b08d0ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old activities table with CASCADE to remove all dependencies
    op.execute('DROP TABLE IF EXISTS activities CASCADE')
    
    # Also drop activity_responses table if it exists (old structure)
    op.execute('DROP TABLE IF EXISTS activity_responses CASCADE')
    
    # Rename new_activities table to activities (this has our JSONB config and proper structure)
    op.rename_table('new_activities', 'activities')


def downgrade() -> None:
    # Rename activities back to new_activities
    op.rename_table('activities', 'new_activities')
