import pyotp
from SmartApi import SmartConnect

# ----------------------------
# Your Angel One credentials
# ----------------------------
API_KEY = "Lp8Wcpst"
CLIENT_CODE = "A919822"
PASSWORD = "2244"
TOTP_SECRET = "AOU4CBV3ZOCFJHLTKJ3UVGGG2Y"   # this must be base32 (no spaces)

# ----------------------------
# Connect to Angel One
# ----------------------------
totp = pyotp.TOTP(TOTP_SECRET)
otp = totp.now()
print("OTP:", otp)

obj = SmartConnect(api_key=API_KEY)
data = obj.generateSession(CLIENT_CODE, PASSWORD, otp)
print("✅ Connected:", data)

# ----------------------------
# Place test order (1 qty ICICI Bank NSE)
# ----------------------------
try:
    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": "ICICIBANK-EQ",  # Angel uses -EQ suffix
        "symboltoken": "4963",            # ICICIBANK token (from Angel)
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",     # 0 for MARKET orders
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
    }

    order_id = obj.placeOrder(order_params)
    print("✅ Order Placed Successfully! ID:", order_id)

except Exception as e:
    print("❌ Order Failed:", str(e))
