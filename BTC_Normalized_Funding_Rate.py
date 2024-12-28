#!/usr/bin/env python
# coding: utf-8

# In[30]:


import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import QuantileTransformer
import time

# Function to fetch funding rate data with pagination
def fetch_binance_funding_rate_paginated(symbol, start_time, end_time=None, limit=1000):
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    funding_data = []
    
    while True:
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "limit": limit
        }
        if end_time:
            params["endTime"] = end_time

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break  # Exit loop if no data is returned
            
            funding_data.extend(data)
            
            # Update start_time to fetch the next set of data
            start_time = data[-1]['fundingTime'] + 1
        else:
            print(f"Failed to fetch funding rate data: {response.status_code}")
            break

        # Break if we have reached the end_time or the API limit
        if len(data) < limit:
            break

    # Convert to DataFrame
    if funding_data:
        df = pd.DataFrame(funding_data)
        df['timestamp'] = pd.to_datetime(df['fundingTime'], unit='ms')
        df['funding_rate'] = pd.to_numeric(df['fundingRate'])
        df.set_index('timestamp', inplace=True)
        return df[['funding_rate']]
    else:
        return None

# Function to fetch BTC price data
def fetch_binance_btc_price(symbol, start_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": start_time,
        "limit": 1000  # Maximum allowed per request
    }
    btc_price_data = []
    
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break  # No more data to fetch
            
            btc_price_data.extend(data)
            
            # Update start_time to fetch the next set of data
            start_time = int(data[-1][0]) + 1  # Move past the last timestamp
        else:
            print(f"Failed to fetch BTC price data: {response.status_code}")
            break

        # Break if fewer than 1000 records are returned
        if len(data) < 1000:
            break

    # Convert to DataFrame
    if btc_price_data:
        df = pd.DataFrame(btc_price_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                                   'close_time', 'quote_asset_volume', 'num_trades', 
                                                   'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['btc_price'] = pd.to_numeric(df['close'])
        df.set_index('timestamp', inplace=True)
        return df[['btc_price']]
    else:
        return None

# Function to quantile normalize funding rates
def quantile_normalize_funding_rate(funding_rate_series):
    quantile_transformer = QuantileTransformer(output_distribution='normal', random_state=42)
    normalized_rates = quantile_transformer.fit_transform(funding_rate_series.values.reshape(-1, 1)).flatten()
    return pd.Series(normalized_rates, index=funding_rate_series.index)

# Fetch funding rate data from 2023 to today
start_time = int(pd.Timestamp("2023-01-01").timestamp() * 1000)
current_time = int(time.time() * 1000)  # Current time in milliseconds

funding_data_paginated = fetch_binance_funding_rate_paginated("BTCUSDT", start_time, current_time)

# Fetch BTC price data from 2023 to today
btc_price_data = fetch_binance_btc_price("BTCUSDT", start_time)

# Merge BTC price data with funding rate data
if funding_data_paginated is not None and btc_price_data is not None:
    combined_data = pd.merge(funding_data_paginated.resample('D').mean(), btc_price_data, left_index=True, right_index=True, how='inner')

    # Quantile normalize the funding rate
    combined_data['funding_rate_normalized'] = quantile_normalize_funding_rate(combined_data['funding_rate'])

    # Identify overbought and oversold areas
    overbought = combined_data['funding_rate_normalized'] > 1.96  # Z-score above 1.96
    oversold = combined_data['funding_rate_normalized'] < -1.96  # Z-score below -1.96

    # Plot the graph
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot BTC price on the primary y-axis
    ax1.set_xlabel('Date')
    ax1.set_ylabel('BTC Price (USD)', color='orange')
    line1, = ax1.plot(combined_data.index, combined_data['btc_price'], label='BTC Price (USD)', color='orange', alpha=0.7)
    ax1.tick_params(axis='y', labelcolor='orange')

    # Plot normalized funding rate on the secondary y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Funding Rate', color='blue')
    line2, = ax2.plot(combined_data.index, combined_data['funding_rate_normalized'], label='Funding Rate', color='blue', alpha=0.7)
    ax2.tick_params(axis='y', labelcolor='blue')

    # Add vertical lines for overbought and oversold areas
    for date in combined_data.index[overbought]:
        ax1.axvline(date, color='red', linestyle='-', alpha=0.7, linewidth=1.5)  # Overbought
    for date in combined_data.index[oversold]:
        ax1.axvline(date, color='green', linestyle='-', alpha=0.7, linewidth=1.5)  # Oversold

    # Add legend
    fig.legend([line1, line2, plt.Line2D([0], [0], color='red', lw=2), plt.Line2D([0], [0], color='green', lw=2)], 
               ['BTC Price (USD)', 'Funding Rate', 'Overbought (Z > 1.96)', 'Oversold (Z < -1.96)'], 
               loc="upper left", bbox_to_anchor=(0.1, 0.9))

    # Title and layout adjustments
    plt.title('Binance BTC Normalized Funding Rate')
    fig.tight_layout()
    plt.show()
else:
    print("Failed to fetch or process BTC price and funding rate data.")


# In[ ]:




