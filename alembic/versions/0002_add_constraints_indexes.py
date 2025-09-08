"""Add unique constraints and composite index

Revision ID: 0002_add_constraints_indexes
Revises: 0001_initial
Create Date: 2025-09-01 12:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_add_constraints_indexes"

down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    # Use batch mode for SQLite compatibility
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        with op.batch_alter_table("portfolio_positions") as batch_op:
            batch_op.create_unique_constraint(
                "uq_portfolio_positions_symbol", ["symbol"]
            )
        with op.batch_alter_table("historical_prices") as batch_op:
            batch_op.create_unique_constraint(
                "uq_historical_prices_symbol_date", ["symbol", "date"]
            )
            batch_op.create_index(
                "ix_historical_prices_symbol_date", ["symbol", "date"]
            )
    else:
        op.create_unique_constraint(
            "uq_portfolio_positions_symbol", "portfolio_positions", ["symbol"]
        )
        op.create_unique_constraint(
            "uq_historical_prices_symbol_date",
            "historical_prices",
            ["symbol", "date"],
        )
        op.create_index(
            "ix_historical_prices_symbol_date",
            "historical_prices",
            ["symbol", "date"],
        )


def downgrade():
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        with op.batch_alter_table("historical_prices") as batch_op:
            batch_op.drop_index("ix_historical_prices_symbol_date")
            batch_op.drop_constraint(
                "uq_historical_prices_symbol_date", type_="unique"
            )
        with op.batch_alter_table("portfolio_positions") as batch_op:
            batch_op.drop_constraint(
                "uq_portfolio_positions_symbol", type_="unique"
            )
    else:
        op.drop_index(
            "ix_historical_prices_symbol_date", table_name="historical_prices"
        )
        op.drop_constraint(
            "uq_historical_prices_symbol_date",
            "historical_prices",
            type_="unique",
        )
        op.drop_constraint(
            "uq_portfolio_positions_symbol",
            "portfolio_positions",
            type_="unique",
        )
