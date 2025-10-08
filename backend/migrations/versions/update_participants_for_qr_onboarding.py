"""Update participants table for QR onboarding

Revision ID: update_participants_qr
Revises: 7b81da24b89f
Create Date: 2025-10-07 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_participants_qr'
down_revision = '7b81da24b89f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop and recreate participants table with new schema
    op.drop_table('participants')
    
    op.create_table('participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()'), index=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nickname', sa.String(length=50), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('connection_data', postgresql.JSONB(astext_type=sa.Text()), default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('session_id', 'nickname', name='unique_session_nickname')
    )
    
    # Update user_responses participant_id to UUID
    op.alter_column('user_responses', 'participant_id',
        existing_type=sa.Integer(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False
    )


def downgrade() -> None:
    # Revert user_responses participant_id to Integer
    op.alter_column('user_responses', 'participant_id',
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        existing_nullable=False
    )
    
    # Restore original participants table structure
    op.drop_table('participants')
    
    op.create_table('participants',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('sessions.id'), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=20), default='participant', nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )