import time, uuid
from .base import Broker

class PaperBroker(Broker):
    def __init__(self):
        self._orders = {}
        self._positions = {}

    def connect(self): pass

    def ltp(self, symbol: str, exchange: str="NSE") -> float:
        return float(self._last_price.get(symbol, 0.0)) if hasattr(self, "_last_price") else 0.0

    def set_price(self, symbol: str, price: float):
        """Update last traded price (from Yahoo / candles)."""
        self._last_price = getattr(self, "_last_price", {})
        self._last_price[symbol] = price

    def place_order(self, **kwargs):
        oid = str(uuid.uuid4())
        price = kwargs.get("price") or self._last_price.get(kwargs["symbol"], 0.0)
        side  = kwargs["side"].upper()
        qty   = kwargs["qty"]

        self._orders[oid] = {**kwargs, "status":"FILLED", "avg_price": price, "time": time.time()}

        pos = self._positions.get(kwargs["symbol"], 0)
        self._positions[kwargs["symbol"]] = pos + (qty if side=="BUY" else -qty)

        return {"order_id": oid, "status":"FILLED", "avg_price": price}

    def order_status(self, order_id): return self._orders.get(order_id, {})
    def positions(self): return self._positions
    def cancel_order(self, order_id): self._orders[order_id]["status"]="CANCELLED"
