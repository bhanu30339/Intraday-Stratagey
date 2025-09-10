from brokers.paper import PaperBroker
from services.angel_broker import AngelBroker

def make_broker(mode, creds):
    if mode == "PAPER":
        return PaperBroker()
    elif mode == "ANGEL_ONE":
        return AngelBroker(creds)
    else:
        raise ValueError("❌ Unknown MODE in secrets.toml")
