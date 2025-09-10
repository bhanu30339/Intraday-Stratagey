from SmartApi import SmartConnect
import pyotp

class AngelBroker:
    def __init__(self, creds):
        self.api_key = creds["api_key"]
        self.client_code = creds["client_code"]
        self.password = creds["password"]
        self.totp_secret = creds["totp_secret"]
        self.conn = None

    def connect(self):
        try:
            self.conn = SmartConnect(api_key=self.api_key)
            token = pyotp.TOTP(self.totp_secret).now()
            data = self.conn.generateSession(self.client_code, self.password, token)
            self.refresh_token = data["data"]["refreshToken"]
            print("✅ Connected to Angel One SmartAPI")
        except Exception as e:
            print("❌ Connection failed:", e)

    def place_order(self, symbol, exchange, qty, side):
        order_type = "BUY" if side.upper() == "BUY" else "SELL"
        try:
            order = self.conn.placeOrder(
                variety="NORMAL",
                tradingsymbol=symbol.replace(".NS", ""),
                symboltoken="3045",  # TODO: fetch from Angel One scrip master
                transactiontype=order_type,
                exchange=exchange,
                ordertype="MARKET",
                producttype="INTRADAY",
                duration="DAY",
                price=0,
                quantity=qty
            )
            print(f"✅ {order_type} order placed:", order)
        except Exception as e:
            print("❌ Order failed:", e)

    def set_price(self, symbol, price):
        # Just for paper trading compatibility
        print(f"📊 Price update: {symbol} = {price}")
