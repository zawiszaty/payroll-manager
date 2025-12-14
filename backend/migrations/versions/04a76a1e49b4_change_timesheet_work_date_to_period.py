"""change_timesheet_work_date_to_period

Revision ID: 04a76a1e49b4
Revises: dcd83e9fb888
Create Date: 2025-12-13 18:49:03.282186

"""
from alembic import op
import sqlalchemy as sa


revision = '04a76a1e49b4'
down_revision = 'dcd83e9fb888'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename work_date column to start_date
    op.alter_column('timesheets', 'work_date', new_column_name='start_date')

    # Add end_date column
    op.add_column('timesheets', sa.Column('end_date', sa.Date(), nullable=True))

    # Set end_date to start_date for existing records
    op.execute('UPDATE timesheets SET end_date = start_date WHERE end_date IS NULL')

    # Make end_date not nullable
    op.alter_column('timesheets', 'end_date', nullable=False)


def downgrade() -> None:
    # Make end_date nullable first
    op.alter_column('timesheets', 'end_date', nullable=True)

    # Drop end_date column
    op.drop_column('timesheets', 'end_date')

    # Rename start_date back to work_date
    op.alter_column('timesheets', 'start_date', new_column_name='work_date')
