"""Initial schema for Wedding Gift Ledger

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-24 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Tables are created via Base.metadata.create_all and tracked by Alembic
    pass

def downgrade() -> None:
    op.drop_table('settings')
    op.drop_table('gift_exchange_history')
    op.drop_table('thank_you_status_history')
    op.drop_table('thank_you_messages')
    op.drop_table('gift_contributors')
    op.drop_table('gifts')
    op.drop_table('guests')
    op.drop_table('wedding_events')
    op.drop_table('users')
