# Personal Finance Management Tool

A comprehensive personal finance management tool built with Python that integrates with PostgreSQL for data persistence.

## Features

- 📊 Portfolio management with real-time stock prices
- 💰 Performance tracking and analysis
- 📈 Historical data storage and retrieval
- 🗄️ PostgreSQL database integration
- 🔄 Automatic data synchronization with Yahoo Finance
- 📱 Modern Python package structure

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MauGx3/personal-finance.git
   cd personal-finance
   ```

2. Install dependencies:

   ```bash
   pip install -e .
   ```

3. Set up PostgreSQL database (optional if you just want to try it quickly with SQLite fallback):

   ```bash
   # Install PostgreSQL if not already installed
   # Create a database named 'personal_finance'
   createdb personal_finance
   ```

4. Configure database connection (or rely on automatic SQLite fallback):

   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your database credentials
   # DATABASE_URL=postgresql://username:password@localhost/personal_finance
   ```

5. Initialize the database:

   ```bash
   python setup_database.py
   ```

## Database Setup

The application prefers PostgreSQL. If `DATABASE_URL` is not provided, it will
automatically fall back to a local SQLite file database `personal_finance.db` so
you can experiment without installing Postgres first.

The schema contains the following tables:

- **tickers**: Stores stock ticker information
- **portfolio_positions**: Stores portfolio holdings
- **historical_prices**: Stores historical price data

### Database Configuration

Set the `DATABASE_URL` environment variable or modify the `.env` file (see
`.env.example`). Example values:

```bash
# Local development
DATABASE_URL=postgresql://localhost/personal_finance

# With credentials
DATABASE_URL=postgresql://user:password@localhost:5432/personal_finance
```

### Running Migrations Programmatically

You can run Alembic migrations from Python without the CLI:

```python
from personal_finance.database import DatabaseManager
db = DatabaseManager()  # picks up DATABASE_URL or falls back to SQLite
db.run_migrations()      # upgrades to head
```

Or via Alembic CLI (uses `alembic.ini`):

```bash
alembic upgrade head
```

## Usage

### Basic Usage

Run the main application:
```bash
python run_finance.py
```

### Database Operations

```python
from personal_finance.database import DatabaseManager
from personal_finance.portfolio import PortfolioManager

# Initialize database connection (loads .env automatically, fallback to SQLite if unset)
db = DatabaseManager()

# Create portfolio manager
pm = PortfolioManager(db)

# Add a position
pm.add_position("AAPL", "Apple Inc.", 10, 150.00, "2023-01-15")

# Get portfolio summary
summary = pm.get_positions_summary()
print(summary)
```

### Yahoo Finance Integration

```python
from personal_finance.yahoo_finance import get_ticker_price, fetch_and_store_historical_data

# Get current price
price = get_ticker_price("AAPL")

# Fetch and store historical data
data = fetch_and_store_historical_data("AAPL", "1y")
```

## Data Migration

If you have existing JSON data files, the setup script will automatically migrate them to PostgreSQL:

```bash
python setup_database.py
```

This will:
- Create all necessary database tables
- Migrate ticker data from `data/tickers.json`
- Migrate portfolio data from `data/portfolio.json`

## API Reference

### DatabaseManager

- `create_tables()`: Create database tables
- `add_or_update_ticker(symbol, name, price)`: Add/update ticker
- `get_ticker(symbol)`: Get ticker by symbol
- `add_portfolio_position(symbol, name, quantity, buy_price, buy_date)`: Add position
- `get_portfolio_positions()`: Get all positions
- `remove_portfolio_position(symbol)`: Remove position

### PortfolioManager

- `add_position(symbol, name, quantity, buy_price, buy_date)`: Add portfolio position
- `remove_position(symbol)`: Remove position
- `get_portfolio_value()`: Calculate total portfolio value
- `get_positions_summary()`: Get detailed position summary
- `get_historical_data(period)`: Get historical data for all positions

## Development

### Project Structure

```
personal-finance/
├── src/personal_finance/
│   ├── __init__.py
│   ├── database.py          # PostgreSQL integration
│   ├── portfolio.py         # Portfolio management
│   ├── yahoo_finance.py     # Yahoo Finance API integration
│   └── data/                # Legacy JSON data (for migration)
├── setup_database.py        # Database initialization script
├── run_finance.py          # Main application entry point
├── pyproject.toml          # Project configuration
└── .env.example            # Environment configuration template
```

### Adding New Features / Schema Changes

1. Define / modify models in `database.py`
2. Generate a new Alembic migration: `alembic revision --autogenerate -m "your message"`
3. Apply migrations: `alembic upgrade head` (or call `DatabaseManager.run_migrations()`)
4. Add helper methods to `DatabaseManager`
5. Update modules to use new DB functionality
6. Adjust docs & tests

## Dependencies

- psycopg2-binary: PostgreSQL adapter
- sqlalchemy: ORM for database operations
- yfinance: Yahoo Finance API
- pandas: Data manipulation
- requests: HTTP requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the CC0 1.0 Universal License.
