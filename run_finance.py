"""
Entry point script for the personal_finance package.
"""

import sys
import os

# Add the src directory to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import personal_finance  # pylint: disable=wrong-import-position # noqa: E402
from personal_finance.database import DatabaseManager
from personal_finance.portfolio import PortfolioManager
from personal_finance.yahoo_finance import update_all_ticker_prices


def main():
    """Main function to demonstrate package functionality."""
    print(f"Running Personal Finance package v{personal_finance.__version__}")
    print(f"Available modules: {', '.join(personal_finance.__all__)}")

    try:
        # Initialize database connection
        db_manager = DatabaseManager()
        print("✓ Database connection established")

        # Create portfolio manager with database integration
        pm = PortfolioManager(db_manager)

        # Load portfolio from database
        pm.load_portfolio()
        print("✓ Portfolio loaded from database")

        # Update ticker prices
        print("Updating ticker prices...")
        updated_count = update_all_ticker_prices(db_manager)
        print(f"✓ Updated prices for {updated_count} tickers")

        # Get portfolio summary
        summary = pm.get_positions_summary()
        if summary:
            print("\n📊 Portfolio Summary:")
            print("-" * 80)
            print("<10")
            print("-" * 80)

            total_value = 0
            total_cost = 0

            for position in summary:
                print("<10")
                total_value += position['market_value']
                total_cost += position['cost_basis']

            print("-" * 80)
            total_gain = total_value - total_cost
            total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0
            print("<10")

        # Get current portfolio value
        portfolio_value = pm.get_portfolio_value()
        print(f"\n💰 Current Portfolio Value: ${portfolio_value:,.2f}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure PostgreSQL is running and the database is set up.")
        print("Run 'python setup_database.py' to initialize the database.")


if __name__ == "__main__":
    main()
