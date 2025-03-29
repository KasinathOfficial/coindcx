import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor")

def fetch_coindcx_data():
    url = "https://api.coindcx.com/exchange/ticker"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return [coin for coin in data if coin['market'].endswith('INR')]  # Filter INR pairs
    except requests.RequestException:
        return []

def calculate_target_price(price, change, volume):
    fib_multiplier = 1.618
    volatility_factor = 1 + (volume / 10000000)
    return round(price * (1 + ((change / 100) * fib_multiplier * volatility_factor)), 2)

def calculate_stop_loss(price, change):
    stop_loss_factor = 0.95 if change > 8 else 0.90
    return round(price * stop_loss_factor, 2)

def calculate_volatility(change, volume):
    return round(abs(change) * (1 + (volume / 10000000)), 2)

def analyze_market(data):
    potential_explosions = []
    for coin in data:
        try:
            symbol = coin['market']
            price = float(coin['last_price'])
            volume = float(coin['volume'])
            change = float(coin['change_24_hour'])

            if change > 5 and volume > 500000:  # Trade filter
                target_price = calculate_target_price(price, change, volume)
                stop_loss_price = calculate_stop_loss(price, change)
                volatility = calculate_volatility(change, volume)

                if volatility > 20:
                    trade_decision = "🔥 High Volatility - Enter with Caution"
                elif volatility > 10:
                    trade_decision = "✅ Strong Buy"
                else:
                    trade_decision = "⚠️ Moderate Buy"

                potential_explosions.append({
                    "Symbol": symbol, "Price": price, "24h Change (%)": change,
                    "Volume": volume, "Volatility (%)": volatility,
                    "Target Price": target_price, "Stop Loss Price": stop_loss_price,
                    "Trade Decision": trade_decision
                })
        except (ValueError, KeyError):
            continue
    return potential_explosions

placeholder = st.empty()
while True:
    data = fetch_coindcx_data()
    if data:
        analyzed_data = analyze_market(data)
        if analyzed_data:
            df = pd.DataFrame(analyzed_data)
            with placeholder.container():
                st.subheader("📈 Cryptos Likely to Explode Soon")
                st.dataframe(df)
        else:
            with placeholder.container():
                st.info("No potential explosive cryptos detected right now.")
    else:
        with placeholder.container():
            st.error("Failed to retrieve data. Please check API access.")
    time.sleep(1)  # Refresh data every second without refreshing the page
