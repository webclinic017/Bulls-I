import numpy as np
import pandas as pd

def rsiFunc(prices, n=14):
    # Returns an RSI array
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n-1)+upval)/n
        down = (down*(n-1)+downval)/n
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    return rsi

def calc_minimum_usable_date(sorted_stock):
    date = sorted_stock.loc[~sorted_stock['day_365'].isna()]['Date'].min()
    return date

def calc_avgs(stock):
    # Sorting the data according to date column
    sorted_stock = stock.sort_values(by=['Date'])
    # Create Target
    sorted_stock['Day1Close'] = sorted_stock.Close.shift(periods=-1, freq=None)
    # Create Features
    sorted_stock['day_5'] = sorted_stock.Close.rolling(5, win_type='triang').mean()
    sorted_stock['day_15'] = sorted_stock.Close.rolling(15, win_type='triang').mean()
    sorted_stock['day_51'] = sorted_stock.Close.rolling(51, win_type='triang').mean()
    sorted_stock['day_84'] = sorted_stock.Close.rolling(84, win_type='triang').mean()
    sorted_stock['day_168'] = sorted_stock.Close.rolling(168, win_type='triang').mean()
    sorted_stock['day_270'] = sorted_stock.Close.rolling(270, win_type='triang').mean()
    sorted_stock['day_365'] = sorted_stock.Close.rolling(365, win_type='triang').mean()
    rsi = rsiFunc(np.asarray(sorted_stock['Close']))
    sorted_stock['rsi'] = rsi
    sorted_stock['rsi_avg_3d'] = sorted_stock['rsi'] - sorted_stock['rsi'].shift(3)
    sorted_stock['rsi_avg_7d'] = sorted_stock['rsi'] - sorted_stock['rsi'].shift(7)
    sorted_stock['rsi_avg_12d'] = sorted_stock['rsi'] - sorted_stock['rsi'].shift(12)
    sorted_stock['rsi_avg_16d'] = sorted_stock['rsi'] - sorted_stock['rsi'].shift(16)
    sorted_stock['rsi_avg_chg'] = (sorted_stock['rsi_avg_3d'] + sorted_stock['rsi_avg_7d'] + sorted_stock['rsi_avg_12d'] + sorted_stock['rsi_avg_16d']) / 4
    date_str = calc_minimum_usable_date(sorted_stock) # Need to select dynamically
    date = pd.to_datetime(date_str, format='%Y-%m-%d', utc=True).tz_convert('Asia/Kolkata')
    clean_stock = sorted_stock[sorted_stock["Date"] > date]
    return clean_stock

def calc_gains(data):
    data

def create_features(data):
    # Convert Date column in datetime format
    data['Date'] = pd.to_datetime(data['Date'])

    data = calc_avgs(data)    
    data = calc_gains(data)
    return data

def feature_engineering(stock_data):
    stock_data = create_features(stock_data)
    return stock_data
