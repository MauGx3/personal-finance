#!/usr/bin/env python3
"""
Database initialization and migration script
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from personal_finance.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database and create tables"""
    logger.info("Initializing database...")

    db_manager = DatabaseManager()

    try:
        # Create all tables
        db_manager.create_tables()
        logger.info("Database tables created successfully")

        return db_manager

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def migrate_existing_data(db_manager: DatabaseManager):
    """Migrate data from JSON files to database"""
    logger.info("Migrating existing data from JSON files...")

    portfolio_file = "src/personal_finance/data/portfolio.json"
    tickers_file = "src/personal_finance/data/tickers.json"

    try:
        db_manager.migrate_json_data(portfolio_file, tickers_file)
        logger.info("Data migration completed successfully")

    except Exception as e:
        logger.error(f"Error during data migration: {e}")
        raise


def main():
    """Main function to run database setup"""
    try:
        # Initialize database
        db_manager = initialize_database()

        # Check if data migration is needed
        portfolio_file = Path("src/personal_finance/data/portfolio.json")
        if portfolio_file.exists():
            migrate_existing_data(db_manager)
        else:
            logger.info("No existing JSON data found, skipping migration")

        logger.info("Database setup completed successfully!")

        # Print some statistics
        tickers = db_manager.get_all_tickers()
        positions = db_manager.get_portfolio_positions()

        logger.info(f"Database contains {len(tickers)} tickers and {len(positions)} portfolio positions")

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
