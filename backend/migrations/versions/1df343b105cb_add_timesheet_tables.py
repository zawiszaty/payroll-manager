"""add_timesheet_tables

Revision ID: 1df343b105cb
Revises: 1f53aa31f645
Create Date: 2025-12-01 11:32:24.014891

"""
from alembic import op
import sqlalchemy as sa


revision = '1df343b105cb'
down_revision = '1f53aa31f645'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'timesheets',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('work_date', sa.Date(), nullable=False),
        sa.Column('hours', sa.Float(), nullable=False),
        sa.Column('overtime_hours', sa.Float(), nullable=False),
        sa.Column('overtime_type', sa.String(length=50), nullable=True),
        sa.Column('project_id', sa.Uuid(), nullable=True),
        sa.Column('task_description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.Date(), nullable=False),
        sa.Column('updated_at', sa.Date(), nullable=False),
        sa.Column('submitted_at', sa.Date(), nullable=True),
        sa.Column('approved_at', sa.Date(), nullable=True),
        sa.Column('approved_by', sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_timesheets_employee_id'), 'timesheets', ['employee_id'], unique=False)
    op.create_index(op.f('ix_timesheets_work_date'), 'timesheets', ['work_date'], unique=False)
    op.create_index(op.f('ix_timesheets_project_id'), 'timesheets', ['project_id'], unique=False)
    op.create_index(op.f('ix_timesheets_status'), 'timesheets', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_timesheets_status'), table_name='timesheets')
    op.drop_index(op.f('ix_timesheets_project_id'), table_name='timesheets')
    op.drop_index(op.f('ix_timesheets_work_date'), table_name='timesheets')
    op.drop_index(op.f('ix_timesheets_employee_id'), table_name='timesheets')
    op.drop_table('timesheets')
