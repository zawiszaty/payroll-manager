"""add_timestamps_to_absence_tables

Revision ID: 3e10dd137943
Revises: adb5581af7ae
Create Date: 2025-11-29 19:20:29.955405

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '3e10dd137943'
down_revision = 'adb5581af7ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at to absences table
    op.add_column('absences', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('absences', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    # Add created_at and updated_at to absence_balances table
    op.add_column('absence_balances', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('absence_balances', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    # Remove timestamps from absence_balances table
    op.drop_column('absence_balances', 'updated_at')
    op.drop_column('absence_balances', 'created_at')
    
    # Remove timestamps from absences table
    op.drop_column('absences', 'updated_at')
    op.drop_column('absences', 'created_at')
