from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Broker(ABC):
    @abstractmethod
    def connect(self) -> None: ...
    @abstractmethod
    def ltp(self, symbol: str, exchange: str="NSE") -> float: ...
    @abstractmethod
    def place_order(self, *, symbol: str, exchange: str, qty: int,
                    side: str, order_type: str="MARKET",
                    product: str="INTRADAY",
                    price: Optional[float]=None,
                    stoploss: Optional[float]=None,
                    target: Optional[float]=None) -> Dict[str, Any]: ...
    @abstractmethod
    def order_status(self, order_id: str) -> Dict[str, Any]: ...
    @abstractmethod
    def positions(self) -> Any: ...
    @abstractmethod
    def cancel_order(self, order_id: str) -> Any: ...
