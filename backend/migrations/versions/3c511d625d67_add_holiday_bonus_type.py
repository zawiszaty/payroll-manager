"""add_holiday_bonus_type

Revision ID: 3c511d625d67
Revises: ffd5019eb51e
Create Date: 2025-11-27 13:54:13.571244

"""
from alembic import op
import sqlalchemy as sa


revision = '3c511d625d67'
down_revision = 'ffd5019eb51e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE bonustype ADD VALUE 'HOLIDAY'")


def downgrade() -> None:
    pass
