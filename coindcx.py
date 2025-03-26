import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Crypto Explosion Predictor", layout="wide")
st.title("🚀 Crypto Explosion Predictor")

@st.cache_data(ttl=10)  # Cache data for 10 seconds to prevent excessive API calls
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

# Live update control
if "run_updates" not in st.session_state:
    st.session_state["run_updates"] = False

def toggle_updates():
    st.session_state["run_updates"] = not st.session_state["run_updates"]

st.button("⏳ Start/Stop Live Updates", on_click=toggle_updates)

# Display real-time data
data_placeholder = st.empty()

while st.session_state["run_updates"]:
    with st.status("Fetching live data... ⏳", expanded=False):
        data = fetch_coindcx_data()
        analyzed_data = analyze_market(data) if data else []

        if analyzed_data:
            df = pd.DataFrame(analyzed_data)
            data_placeholder.subheader("📈 Cryptos Likely to Explode Soon")
            data_placeholder.dataframe(df)
        else:
            data_placeholder.info("No potential explosive cryptos detected right now.")

    time.sleep(5)  # Fetch new data every 5 seconds
