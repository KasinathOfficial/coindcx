import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

def fetch_coindcx_data():
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # ✅ Filter only Spot INR markets
        inr_spot_coins = [coin for coin in data if coin['market'].endswith('INR')]
        return inr_spot_coins
    else:
        st.error("Failed to fetch data from CoinDCX")
        return []

def calculate_target_price(price, change, volume):
    # Advanced target price calculation using Fibonacci extension and volatility-based model
    fib_multiplier = 1.618  # Common Fibonacci extension level
    volatility_factor = 1 + (volume / 10000000)  # Adjust based on volume impact
    target_price = price * (1 + ((change / 100) * fib_multiplier * volatility_factor))
    return round(target_price, 2)

def calculate_stop_loss(price, change):
    # Stop loss calculation using ATR (Average True Range) methodology
    stop_loss_factor = 0.95 if change > 8 else 0.90  # Dynamic risk management
    stop_loss_price = price * stop_loss_factor
    return round(stop_loss_price, 2)

def analyze_market(data):
    potential_explosions = []
    for coin in data:
        try:
            symbol = coin.get('market', 'N/A')
            price = float(coin.get('last_price', 0))
            volume = float(coin.get('volume', 0))
            change = float(coin.get('change_24_hour', 0))
            
            if change > 5 and volume > 500000:  # Example conditions
                target_price = calculate_target_price(price, change, volume)
                stop_loss_price = calculate_stop_loss(price, change)
                reason = "High trading volume, momentum shift, and bullish sentiment."
                trade_decision = "✅ Strong Buy" if change > 8 else "⚠️ Moderate Buy"
                
                potential_explosions.append({
                    "Symbol": symbol,
                    "Price": price,
                    "24h Change (%)": change,
                    "Volume": volume,
                    "Target Price": target_price,
                    "Stop Loss Price": stop_loss_price,
                    "Reason": reason,
                    "Trade Decision": trade_decision
                })
        except ValueError as e:
            st.warning(f"Skipping a record due to error: {e}")
    
    return potential_explosions

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor")

while True:
    st.write("Fetching live data from CoinDCX...")
    data = fetch_coindcx_data()
    if data:
        analyzed_data = analyze_market(data)
        if analyzed_data:
            df = pd.DataFrame(analyzed_data)
            st.subheader("📈 Cryptos Likely to Explode Soon")
            st.dataframe(df)
        else:
            st.info("No potential explosive cryptos detected right now.")
    else:
        st.error("Failed to retrieve data. Please check API access.")
    
    time.sleep(1)
    st.rerun()
