# stockdex shim moved from top-level _stockdex.py
# Provide wrapper functions used by the codebase

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Ticker:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_last_close(self):
        # Placeholder implementation — original library may provide richer data
        # In the original _stockdex module this called into an external library
        logger.debug(
            f"Ticker.get_last_close({self.symbol}) called — placeholder returning 0"
        )
        return 0


def get_last_close(symbol: str) -> Optional[float]:
    t = Ticker(symbol)
    return t.get_last_close()
