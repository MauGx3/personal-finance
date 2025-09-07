import logging
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
try:
    import stockdex as sd
except ImportError:
    sd = None  # stockdex not available
from .database import DatabaseManager, PortfolioPosition

# import yahoo_finance as yf

# Configure basic logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass
class Portfolio:
    positions: dict
    classes: str

    @dataclass
    class Position:
        symbol: str
        quantity: float
        cost_basis: float = 0.0

    def __post_init__(self):
        self.positions = {}
        self.classes = ""


class PortfolioManager:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or DatabaseManager()
        self.portfolio = {}  # Keep for backward compatibility, but will be deprecated

    def load_portfolio(self, file_path: str = None):
        """Load portfolio from database or JSON file for migration"""
        if file_path:
            # Legacy JSON loading for migration
            try:
                with open(file_path, encoding="utf-8") as file:
                    data = json.load(file)
                    self.portfolio = data
            except FileNotFoundError as e:
                logging.error("Portfolio file not found: %s", e)
            except json.JSONDecodeError as e:
                logging.error("Invalid JSON in portfolio file: %s", e)
        else:
            # Load from database
            positions = self.db_manager.get_portfolio_positions()
            self.portfolio = {
                "tickers": [
                    {
                        "symbol": pos.symbol,
                        "name": pos.name,
                        "quantity": pos.quantity,
                        "buyPrice": pos.buy_price,
                        "buyDate": pos.buy_date.strftime("%Y-%m-%d")
                    } for pos in positions
                ]
            }

    def add_position(self, symbol: str, name: str, quantity: float, buy_price: float, buy_date: str):
        """Add or update a position in the portfolio"""
        try:
            buy_date_obj = datetime.strptime(buy_date, "%Y-%m-%d")

            # Check if position already exists
            existing_position = self.db_manager.get_portfolio_position(symbol)
            if existing_position:
                # Update existing position
                self.db_manager.update_portfolio_position(
                    symbol=symbol,
                    quantity=quantity,
                    buy_price=buy_price,
                    buy_date=buy_date_obj
                )
            else:
                # Add new position
                self.db_manager.add_portfolio_position(
                    symbol=symbol,
                    name=name,
                    quantity=quantity,
                    buy_price=buy_price,
                    buy_date=buy_date_obj
                )

            # Update ticker info
            self.db_manager.add_or_update_ticker(symbol, name)

            logging.info(f"Added/Updated position: {symbol} - {quantity} shares")

        except Exception as e:
            logging.error(f"Error adding position {symbol}: {e}")
            raise

    def remove_position(self, symbol: str):
        """Remove a position from the portfolio"""
        try:
            success = self.db_manager.remove_portfolio_position(symbol)
            if success:
                logging.info(f"Removed position: {symbol}")
            else:
                logging.warning(f"Position {symbol} not found")
        except Exception as e:
            logging.error(f"Error removing position {symbol}: {e}")
            raise

    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all positions"""
        prices = {}
        positions = self.db_manager.get_portfolio_positions()

        if not positions:
            return prices

        for position in positions:
            try:
                logging.debug("Fetching price for %s", position.symbol)
                if sd is not None:
                    ticker = sd.Ticker(ticker=position.symbol)
                    price_data = ticker.yahoo_api_price(range="1d", dataGranularity="1d")

                    # Extract the latest price
                    if price_data and 'Close' in price_data:
                        latest_price = price_data['Close'].iloc[-1]
                        prices[position.symbol] = latest_price

                        # Update ticker price in database
                        self.db_manager.add_or_update_ticker(
                            position.symbol, position.name, latest_price
                        )
                else:
                    logging.warning("stockdex not available, cannot fetch price for %s", position.symbol)
                    prices[position.symbol] = 0.0

            except Exception as e:
                logging.error("Error fetching price for %s: %s", position.symbol, str(e))
                prices[position.symbol] = 0.0

        return prices

    def get_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        prices = self.get_current_prices()
        total_value = 0.0

        positions = self.db_manager.get_portfolio_positions()
        for position in positions:
            price = prices.get(position.symbol, 0.0)
            total_value += price * position.quantity

        return total_value

    def get_historical_data(self, period="1y") -> Dict[str, Any]:
        """Get historical data for all positions"""
        historical_data = {}
        positions = self.db_manager.get_portfolio_positions()

        if not positions:
            return historical_data

        for position in positions:
            try:
                if sd is not None:
                    ticker = sd.Ticker(position.symbol)
                    data = ticker.yahoo_api_price(range=period, dataGranularity="1d")
                    historical_data[position.symbol] = data

                    # Store historical data in database
                    if data is not None and not data.empty:
                        for date, row in data.iterrows():
                            self.db_manager.add_historical_price(
                                symbol=position.symbol,
                                date=date.to_pydatetime(),
                                open_price=row.get('Open'),
                                high_price=row.get('High'),
                                low_price=row.get('Low'),
                                close_price=row.get('Close'),
                                volume=row.get('Volume')
                            )
                else:
                    logging.warning("stockdex not available, cannot fetch historical data for %s", position.symbol)
                    historical_data[position.symbol] = None

            except Exception as e:
                logging.error(
                    "Error fetching historical data for %s: %s", position.symbol, str(e)
                )

        return historical_data

    def get_positions_summary(self) -> List[Dict]:
        """Get summary of all positions with current values"""
        positions = self.db_manager.get_portfolio_positions()
        prices = self.get_current_prices()

        summary = []
        for position in positions:
            current_price = prices.get(position.symbol, 0.0)
            market_value = current_price * position.quantity
            cost_basis = position.buy_price * position.quantity
            gain_loss = market_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

            summary.append({
                "symbol": position.symbol,
                "name": position.name,
                "quantity": position.quantity,
                "buy_price": position.buy_price,
                "current_price": current_price,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "gain_loss": gain_loss,
                "gain_loss_pct": gain_loss_pct,
                "buy_date": position.buy_date.strftime("%Y-%m-%d")
            })

        return summary


def main():
    # Example usage
    pm = PortfolioManager()
    pm.load_portfolio("src/personal_finance/data/portfolio.json")
    print(pm.portfolio)

    try:
        portfolio_value = pm.get_portfolio_value()
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
    except Exception as e:
        print(f"Error calculating portfolio value: {e}")


if __name__ == "__main__":
    main()
