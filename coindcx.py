import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor")

@st.cache_data(ttl=30)  # Cache data for 30 seconds to reduce API calls
def fetch_coindcx_data():
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return [coin for coin in data if coin['market'].endswith('INR')]  # Filter INR pairs
    else:
        return []

def calculate_target_price(price, change, volume):
    fib_multiplier = 1.618
    volatility_factor = 1 + (volume / 10000000)
    return round(price * (1 + ((change / 100) * fib_multiplier * volatility_factor)), 2)

def calculate_stop_loss(price, change):
    stop_loss_factor = 0.95 if change > 8 else 0.90
    return round(price * stop_loss_factor, 2)

def calculate_volatility(change, volume):
    # Volatility percentage calculation (Relative Change * Volume Impact)
    volatility = abs(change) * (1 + (volume / 10000000))  
    return round(volatility, 2)

def analyze_market(data):
    potential_explosions = []
    for coin in data:
        try:
            symbol = coin.get('market', 'N/A')
            price = float(coin.get('last_price', 0))
            volume = float(coin.get('volume', 0))
            change = float(coin.get('change_24_hour', 0))

            if change > 5 and volume > 500000:
                target_price = calculate_target_price(price, change, volume)
                stop_loss_price = calculate_stop_loss(price, change)
                volatility = calculate_volatility(change, volume)

                # Decision-making using volatility
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
        except ValueError:
            continue
    return potential_explosions

# Fetch and display data
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

# Auto-refresh every 30 seconds
time.sleep(1)
st.rerun()
