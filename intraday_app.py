# import streamlit as st
# import pyotp
# import pandas as pd
# import plotly.graph_objects as go
# from SmartApi import SmartConnect
# import yfinance as yf
# import datetime

# # ------------------------
# # Load secrets
# # ------------------------
# MODE = st.secrets["MODE"]
# ANGEL_API_KEY = st.secrets["ANGEL_API_KEY"]
# ANGEL_CLIENT_CODE = st.secrets["ANGEL_CLIENT_CODE"]
# ANGEL_PASSWORD = st.secrets["ANGEL_PASSWORD"]
# ANGEL_TOTP_SECRET = st.secrets["ANGEL_TOTP_SECRET"]

# # ------------------------
# # Login Function
# # ------------------------
# @st.cache_resource
# def angel_login():
#     totp = pyotp.TOTP(ANGEL_TOTP_SECRET)
#     otp = totp.now()
#     obj = SmartConnect(api_key=ANGEL_API_KEY)
#     obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, otp)
#     st.success("✅ Connected to Angel One SmartAPI")
#     return obj

# smart_api = angel_login()

# # ------------------------
# # Load Scrip Master (cached)
# # ------------------------
# @st.cache_data
# def load_scrip_master():
#     try:
#         df = pd.read_csv(
#             "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.csv"
#         )
#         return df
#     except Exception as e:
#         st.error(f"Error loading scrip master: {e}")
#         return pd.DataFrame()

# scrip_df = load_scrip_master()

# # ------------------------
# # Get Symbol Token dynamically
# # ------------------------
# def get_symbol_details(symbol):
#     try:
#         data = smart_api.searchScrip("NSE", symbol)
#         if "data" in data and len(data["data"]) > 0:
#             # Prefer EQ series
#             eq_scrips = [s for s in data["data"] if s["tradingsymbol"].endswith("-EQ")]
#             if eq_scrips:
#                 scrip = eq_scrips[0]
#             else:
#                 scrip = data["data"][0]  # fallback to first
#             return scrip["symboltoken"], scrip["tradingsymbol"]
#         else:
#             st.error("❌ Symbol not found.")
#             return None, None
#     except Exception as e:
#         st.error(f"Error fetching symbol details: {e}")
#         return None, None

# # ------------------------
# # Get Live Price
# # ------------------------
# def get_ltp(symbol):
#     token, tradingsymbol = get_symbol_details(symbol)
#     if not token:
#         return None
#     try:
#         data = smart_api.ltpData("NSE", tradingsymbol, str(token))
#         return data["data"]["ltp"]
#     except Exception as e:
#         st.error(f"Error fetching price: {e}")
#         return None

# # ------------------------
# # Streamlit UI
# # ------------------------
# st.title("📊 Intraday Trading App")

# # Stock & Qty input
# stock = st.text_input("Enter Stock Symbol (NSE)", "ICICIBANK")
# qty = st.number_input("Quantity", min_value=1, value=1)

# # Show Live Price
# ltp = get_ltp(stock)
# if ltp:
#     st.metric("Live Price", f"₹ {ltp}")

# # ------------------------
# # Place Orders
# # ------------------------
# def place_order(transaction_type, price=0, stoploss=0, target=0):
#     token, tradingsymbol = get_symbol_details(stock)
#     if not token:
#         return
#     try:
#         orderparams = {
#             "variety": "NORMAL",
#             "tradingsymbol": tradingsymbol,
#             "symboltoken": str(token),
#             "transactiontype": transaction_type,
#             "exchange": "NSE",
#             "ordertype": "MARKET" if price == 0 else "LIMIT",
#             "producttype": "INTRADAY",
#             "duration": "DAY",
#             "price": price,
#             "squareoff": str(target),
#             "stoploss": str(stoploss),
#             "quantity": qty,
#         }
#         orderId = smart_api.placeOrder(orderparams)
#         st.success(f"✅ {transaction_type} Order Placed! ID: {orderId}")
#     except Exception as e:
#         st.error(f"❌ Order failed: {e}")

# # Order Buttons
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("🟢 BUY"):
#         place_order("BUY")
# with col2:
#     if st.button("🔴 SELL"):
#         place_order("SELL")

# # ------------------------
# # Order Book
# # ------------------------
# st.subheader("📒 Order Book")
# try:
#     orders = smart_api.orderBook()
#     if "data" in orders and orders["data"]:
#         df_orders = pd.DataFrame(orders["data"])
#         st.dataframe(df_orders)  # <-- show all available columns
#     else:
#         st.info("No orders found.")
# except Exception as e:
#     st.error(f"Error fetching order book: {e}")

# # ------------------------
# # Open Positions
# # ------------------------
# st.subheader("📌 Open Positions")
# try:
#     positions = smart_api.position()
#     if "data" in positions and positions["data"]:
#         df_pos = pd.DataFrame(positions["data"])
#         st.dataframe(df_pos)  # <-- show all available columns
#     else:
#         st.info("No positions found.")
# except Exception as e:
#     st.error(f"Error fetching positions: {e}")


# # ------------------------
# # Candlestick Chart
# # ------------------------
# st.subheader("📈 Price Chart (Last 5 days, 5min)")

# end = datetime.datetime.now()
# start = end - datetime.timedelta(days=5)
# data = yf.download(f"{stock}.NS", start=start, end=end, interval="5m")

# if not data.empty:
#     data["SMA20"] = data["Close"].rolling(20).mean()
#     data["SMA50"] = data["Close"].rolling(50).mean()

#     fig = go.Figure(
#         data=[go.Candlestick(
#             x=data.index,
#             open=data["Open"],
#             high=data["High"],
#             low=data["Low"],
#             close=data["Close"],
#             name="Candlestick"
#         )]
#     )
#     fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], line=dict(color="blue"), name="SMA20"))
#     fig.add_trace(go.Scatter(x=data.index, y=data["SMA50"], line=dict(color="red"), name="SMA50"))
#     st.plotly_chart(fig)
# else:
#     st.warning("No chart data available for this stock.")


import streamlit as st
import pyotp
import pandas as pd
import plotly.graph_objects as go
from SmartApi import SmartConnect
import yfinance as yf
import datetime
import ta
import pytz
from streamlit_autorefresh import st_autorefresh


# ------------------------
# Initialize states if not present
# ------------------------
if "last_trade" not in st.session_state:
    st.session_state["last_trade"] = None  # 'BUY', 'SELL', or None


if "square_off_done" not in st.session_state:
    st.session_state["square_off_done"] = False


# ------------------------
# Constants for Square-off
# ------------------------
SQUARE_OFF_TIME = datetime.time(hour=15, minute=15)  # 3:15 PM IST
IST = pytz.timezone("Asia/Kolkata")


# ------------------------
# Load secrets
# ------------------------
MODE = st.secrets["MODE"]
ANGEL_API_KEY = st.secrets["ANGEL_API_KEY"]
ANGEL_CLIENT_CODE = st.secrets["ANGEL_CLIENT_CODE"]
ANGEL_PASSWORD = st.secrets["ANGEL_PASSWORD"]
ANGEL_TOTP_SECRET = st.secrets["ANGEL_TOTP_SECRET"]


# ------------------------
# Login Function
# ------------------------
@st.cache_resource
def angel_login():
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET)
    otp = totp.now()
    obj = SmartConnect(api_key=ANGEL_API_KEY)
    obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, otp)
    st.success("✅ Connected to Angel One SmartAPI")
    return obj


smart_api = angel_login()


# ------------------------
# Symbol Lookup with Caching
# ------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def get_symbol_details(symbol: str):
    try:
        data = smart_api.searchScrip("NSE", symbol.upper())
        if "data" in data and len(data["data"]) > 0:
            eq_scrips = [s for s in data["data"] if s["tradingsymbol"].endswith("-EQ")]
            scrip = eq_scrips[0] if eq_scrips else data["data"][0]
            return scrip["symboltoken"], scrip["tradingsymbol"]
        st.error("❌ Symbol not found in AngelOne.")
        return None, None
    except Exception as e:
        st.error(f"Error fetching symbol details: {e}")
        return None, None


# ------------------------
# Get Live Price (not cached for intraday trading)
# ------------------------
def get_ltp(symbol):
    token, tradingsymbol = get_symbol_details(symbol)
    if not token:
        return None
    try:
        data = smart_api.ltpData("NSE", tradingsymbol, str(token))
        return data["data"]["ltp"]
    except Exception as e:
        st.error(f"Error fetching price: {e}")
        return None


# ------------------------
# Calculate quantity based on capital, risk %, stoploss %, and LTP
# ------------------------
def calculate_qty(capital, risk_pct, stoploss_pct, ltp):
    if ltp is None or stoploss_pct == 0:
        return 0
    risk_amount = capital * (risk_pct / 100)
    risk_per_share = ltp * (stoploss_pct / 100)
    qty = int(risk_amount / risk_per_share)
    return max(qty, 1)  # minimum 1 share


# ------------------------
# Place Orders
# ------------------------
def place_order(transaction_type, qty, stoploss_pct, target_pct):
    token, tradingsymbol = get_symbol_details(stock)
    if not token:
        return
    if qty <= 0:
        st.error("Calculated quantity is zero! Check your risk, capital, or price.")
        return
    try:
        ltp = get_ltp(stock)
        if not ltp:
            return
        # Calculate SL & Target
        if transaction_type == "BUY":
            stoploss_price = round(ltp * (1 - stoploss_pct / 100), 2)
            target_price = round(ltp * (1 + target_pct / 100), 2)
        else:  # SELL
            stoploss_price = round(ltp * (1 + stoploss_pct / 100), 2)
            target_price = round(ltp * (1 - target_pct / 100), 2)
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": str(token),
            "transactiontype": transaction_type,
            "exchange": "NSE",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": 0,
            "squareoff": str(target_price),
            "stoploss": str(stoploss_price),
            "quantity": qty,
        }
        orderId = smart_api.placeOrder(orderparams)
        st.success(f"✅ {transaction_type} Order Placed | SL={stoploss_price}, Target={target_price}, ID={orderId}")
    except Exception as e:
        st.error(f"❌ Order failed: {e}")


# ------------------------
# Safe float conversion helper
# ------------------------
def safe_float(val):
    if isinstance(val, pd.Series):
        val = val.dropna()
        if not val.empty:
            val = val.iloc[0]
        else:
            return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


# ------------------------
# Caching positions and order book for 1 minute
# ------------------------
@st.cache_data(ttl=60, show_spinner=False)
def cached_positions():
    try:
        return smart_api.position()
    except Exception as e:
        st.error(f"API rate-limit or error fetching positions: {e}")
        return None


@st.cache_data(ttl=60, show_spinner=False)
def cached_order_book():
    try:
        return smart_api.orderBook()
    except Exception as e:
        st.error(f"API rate-limit or error fetching orders: {e}")
        return None


# ------------------------
# Auto square-off function
# ------------------------
def auto_square_off():
    positions_response = cached_positions()
    if positions_response and "data" in positions_response and positions_response["data"]:
        df_pos = pd.DataFrame(positions_response["data"])
        df_pos = df_pos[df_pos["netqty"].astype(float) != 0]
        if df_pos.empty:
            st.info("No positions for auto square-off.")
            return
        for _, row in df_pos.iterrows():
            symbol = row["tradingsymbol"]
            qty = abs(int(float(row["netqty"])))
            side = "SELL" if float(row["netqty"]) > 0 else "BUY"  # close long with SELL, short with BUY
            st.info(f"Auto square-off: Exiting {symbol}, Qty: {qty}, Side: {side}")
            place_order(side, qty, stoploss_pct, target_pct)
    else:
        st.info("No positions found for auto square-off.")


# ------------------------
# Streamlit UI Setup
# ------------------------
st.title("📊 Intraday Trading App")


# Reset button for debugging stuck state
if st.button("Reset last trade state (debug)"):
    st.session_state["last_trade"] = None


stock = st.text_input("Enter Stock Symbol (NSE)", "ICICIBANK")
stoploss_pct = st.number_input("Stoploss %", min_value=0.1, max_value=20.0, value=1.0, step=0.1)
target_pct = st.number_input("Target %", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
capital = st.number_input("Available Capital (₹)", min_value=1000, value=10000, step=500)
risk_pct = st.number_input("Risk % per Trade", min_value=0.1, max_value=5.0, value=1.0, step=0.1)


ltp = get_ltp(stock)
if ltp:
    st.metric("Live Price", f"₹ {ltp}")
    qty = calculate_qty(capital, risk_pct, stoploss_pct, ltp)
    st.metric("Calculated Quantity", qty)
else:
    qty = 0


# Manual Order Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🟢 BUY"):
        place_order("BUY", qty, stoploss_pct, target_pct)
with col2:
    if st.button("🔴 SELL"):
        place_order("SELL", qty, stoploss_pct, target_pct)


# Auto-trade toggle
st.subheader("🤖 Strategy Automation")
auto_trade = st.toggle("Enable Auto-Trade (SMA + RSI)")


# Auto refresh every 10 seconds
st_autorefresh(interval=10 * 1000, limit=None, key="refresh")


# Check current IST time for square-off
now = datetime.datetime.now(IST).time()
if auto_trade:
    if now >= SQUARE_OFF_TIME and not st.session_state["square_off_done"]:
        auto_square_off()
        st.session_state["square_off_done"] = True
        st.success("All positions squared off for the day.")
    elif now < SQUARE_OFF_TIME:
        st.session_state["square_off_done"] = False  # reset for next day


# Chart & Indicators
end = datetime.datetime.now()
start = end - datetime.timedelta(days=5)
data = yf.download(f"{stock}.NS", start=start, end=end, interval="5m")
if not data.empty:
    data["SMA20"] = data["Close"].rolling(20).mean()
    data["SMA50"] = data["Close"].rolling(50).mean()
    close_series = data["Close"].squeeze()
    data["RSI"] = ta.momentum.RSIIndicator(close_series, window=14).rsi()
    latest = data.iloc[-1]
    sma20 = safe_float(latest["SMA20"])
    sma50 = safe_float(latest["SMA50"])
    rsi = safe_float(latest["RSI"])
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Candlestick"
    ))
    fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], line=dict(color="blue"), name="SMA20"))
    fig.add_trace(go.Scatter(x=data.index, y=data["SMA50"], line=dict(color="red"), name="SMA50"))
    st.plotly_chart(fig)
    st.line_chart(data["RSI"], height=200)
    if auto_trade and sma20 is not None and sma50 is not None and rsi is not None:
        prev_sma20 = safe_float(data.iloc[-2]["SMA20"])
        prev_sma50 = safe_float(data.iloc[-2]["SMA50"])
        st.warning(f"DEBUG: prev_sma20={prev_sma20}, prev_sma50={prev_sma50}, sma20={sma20}, sma50={sma50}, last_trade={st.session_state['last_trade']}, qty={qty}")
        if prev_sma20 < prev_sma50 and sma20 > sma50 and st.session_state["last_trade"] != "BUY":
            st.info("SMA20 crossed above SMA50 → BUY Signal Triggered")
            place_order("BUY", qty, stoploss_pct, target_pct)
            st.session_state["last_trade"] = "BUY"
        elif prev_sma20 > prev_sma50 and sma20 < sma50 and st.session_state["last_trade"] != "SELL":
            st.info("SMA20 crossed below SMA50 → SELL Signal Triggered")
            place_order("SELL", qty, stoploss_pct, target_pct)
            st.session_state["last_trade"] = "SELL"
        else:
            st.info("Signal active, no new order placed.")
else:
    st.warning("No chart data available for this stock.")


# Display Orders
st.subheader("📒 Order Book")
orders = cached_order_book()
if orders and "data" in orders and orders["data"]:
    st.dataframe(pd.DataFrame(orders["data"]))
else:
    st.info("No orders found or API rate-limit reached.")


# Display Open Positions
st.subheader("📌 Open Positions")
positions = cached_positions()
if positions and "data" in positions and positions["data"]:
    st.dataframe(pd.DataFrame(positions["data"]))
else:
    st.info("No positions found or API rate-limit reached.")


# Manual Position Exit Section
st.subheader("🛑 Manual Position Exit")
positions_response = cached_positions()
if positions_response and "data" in positions_response and positions_response["data"]:
    df_pos = pd.DataFrame(positions_response["data"])
    df_pos = df_pos[df_pos["netqty"].astype(float) != 0]
    if not df_pos.empty:
        for idx, row in df_pos.iterrows():
            symbol = row["tradingsymbol"]
            qty = abs(int(float(row["netqty"])))
            side = "SELL" if float(row["netqty"]) > 0 else "BUY"
            st.write(f"Position: {symbol}, Qty: {qty}, Side: {side}")
            if st.button(f"Exit {symbol}", key=f"exit_{idx}"):
                st.info(f"Exiting position for {symbol}...")
                place_order(side, qty, stoploss_pct, target_pct)
                st.success(f"Exit order placed for {symbol}")
    else:
        st.info("No open positions to exit.")
else:
    st.info("No positions found or API rate-limit reached.")
