import streamlit as st
import requests
import pandas as pd
import time
import random  # Simulating win probability and average volume

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

def calculate_win_probability(change, volume):
    base_win_rate = 50  # Base probability of a trade winning
    momentum_boost = min(change * 2, 20)  # Cap at 20%
    volume_boost = min((volume / 10000000) * 10, 30)  # Cap at 30%
    total_probability = base_win_rate + momentum_boost + volume_boost
    return round(min(total_probability, 95), 2)  # Cap at 95%

def calculate_best_buy_price(price):
    return round(price * 0.98, 2)  # Buy at 2% discount

def get_volume_type(change, current_volume):
    # Simulated average volume between 60–90% of current volume
    avg_volume = current_volume * random.uniform(0.6, 0.9)

    if current_volume > avg_volume * 1.2:  # Significant spike
        if change > 0:
            return "Bullish"
        elif change < 0:
            return "Bearish"
    return "Neutral"

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
                win_probability = calculate_win_probability(change, volume)
                best_buy_price = calculate_best_buy_price(price)

                volume_type = get_volume_type(change, volume)

                if win_probability > 80:
                    trade_decision = "🔥 High Confidence Buy "
                elif win_probability > 65:
                    trade_decision = "✅ Strong Buy "
                else:
                    trade_decision = "⚠️ Moderate Buy "

                potential_explosions.append({
                    "Symbol": symbol,
                    "Price": price,
                    "Best Price to Buy": best_buy_price,
                    "24h Change (%)": change,
                    "Volume": volume,
                    "Volume Type": volume_type,
                    "Volatility (%)": volatility,
                    "Target Price": target_price,
                    "Stop Loss Price": stop_loss_price,
                    "Win Probability (%)": win_probability,
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

    time.sleep(1)  # Auto-refresh every second
