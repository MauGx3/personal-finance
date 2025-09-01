"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tickers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=10), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'portfolio_positions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('buy_price', sa.Float(), nullable=False),
        sa.Column('buy_date', sa.DateTime(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'historical_prices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('open_price', sa.Float(), nullable=True),
        sa.Column('high_price', sa.Float(), nullable=True),
        sa.Column('low_price', sa.Float(), nullable=True),
        sa.Column('close_price', sa.Float(), nullable=True),
        sa.Column('volume', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('historical_prices')
    op.drop_table('portfolio_positions')
    op.drop_table('tickers')
