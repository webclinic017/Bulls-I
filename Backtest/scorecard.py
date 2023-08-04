import pandas as pd
import numpy as np

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


def count_highs(stock_data, column_name, period):
    # Convert 'Date' column to datetime type
    stock_data['Date'] = pd.to_datetime(stock_data['Date'])

    # Sort the data by date in ascending order
    stock_data.sort_values(by='Date', inplace=True)

    # Create a new column to keep track of the higher highs count
    stock_data['Higher_' + column_name + 's_Count'] = 0

    # Loop through each row in the DataFrame
    for index, row in stock_data.iterrows():
        # Get the index range for the last 13 rows from the current row
        start_index = max(0, index - period)
        end_index = index

        # Filter the DataFrame to get the data within the index range
        relevant_data = stock_data.iloc[start_index:end_index + 1]

        num_higher_highs = 0
        higher_high = 0
        for idx, row2 in relevant_data.iterrows():
            if row2[column_name] > higher_high:
                if higher_high == 0:
                    higher_high = row2[column_name]
                else:
                    higher_high = row2[column_name]
                    num_higher_highs += 1
        
        # Update the 'Higher_Highs_Count' column for the current row
        stock_data.at[index, 'Higher_' + column_name + 's_Count_' + str(period) + 'days'] = num_higher_highs
    return stock_data

def calc_ema(data, span):
    data["ema_" + str(span)] = data['Close'].ewm(span=span, adjust=False).mean()
    return data

def calc_52wh_by_cmp(data):
    data['High52W'] = 0
    for index, row in data.iterrows():
        start_idx = index - max(0, index - 364)
        end_idx = index
        relevant_data = data.iloc[start_idx:end_idx + 1]
        data.at[index, 'High52W'] = relevant_data['Close'].max()
    data['Cmp_by_High52W'] = data['Close'] / data['High52W']
    return data

def volume_growth(data, period):
    for index, row in data.iterrows():
        last7thdayidx = max(0, index - period)
        val = data.iloc[last7thdayidx]['Volume']
        if val == 0:
            while val == 0:
                last7thdayidx += 1
                val = data.iloc[last7thdayidx]['Volume']
        data.at[index, 'last7thdayVol'] = val
    data['VolumeGrowth' + str(period) + 'D'] = (data['Volume'] - data['last7thdayVol']) / data['last7thdayVol']
    return data

def open_vs_close(data, period):
    for index, row in data.iterrows():
        start_idx = max(0, index - period)
        end_idx = index
        relevant_data = data.iloc[start_idx: end_idx]
        closeGreaterThanOpenCount = 0
        for idx, row2 in relevant_data.iterrows():
            if row2['Close'] > row2['Open']:
                closeGreaterThanOpenCount += 1
        data.at[index, 'closeGreaterThanOpenCount'+str(period)+'days'] = closeGreaterThanOpenCount
    return data

def calc_ratio_ema(data, short, long):
    data = calc_ema(data, short)
    data = calc_ema(data, long)
    data[str(short) + 'ema_by_' + str(long) + 'ema'] = data["ema_" + str(short)] / data["ema_" + str(long)]
    return data

features = {
            'rsi': [['<30','30-40','40-60','60-70','>70'], [20, 15, 15, 10, 5], 0.09090909091], 
            'Higher_Highs_Count_14days': [['<1','1-5','5-10','>10'], [5, 10, 15, 25], 0.09090909091], 
            'Higher_Highs_Count_7days': [['<1','1-3','3-5','>5'], [5, 10, 15, 25], 0.09090909091],
            'Higher_Lows_Count_14days': [['<1','1-5','5-10','>10'], [5, 10, 15, 25], 0.09090909091],
            'Higher_Lows_Count_7days': [['<1','1-3','3-5','>5'], [5, 10, 15, 25], 0.09090909091],

            '50ema_by_200ema': [['<0.8','0.8-0.9','0.9-1.0','>1.0'], [5, 10, 15, 20], 0.09090909091],
            '20ema_by_50ema': [['<0.85','0.85-0.95','0.95-1.0','>1.0'], [5, 10, 15, 20], 0.09090909091],
            '5ema_by_20ema': [['<0.9','0.9-0.95','0.95-1.0','>1.0'], [5, 10, 15, 20], 0.09090909091],
            'Cmp_by_High52W': [['<1.0','1.0-1.1','1.0-1.2','1.2-1.3','>1.3'], [20, 20, 15, 15, 10], 0.09090909091], ###
            'VolumeGrowth7D': [['<1.0','1.0-1.1','1.1-1.2','>1.2'], [5, 10, 15, 20], 0.09090909091],
            'closeGreaterThanOpenCount7days': [['<1','1-3','3-5','>5'], [20, 15, 10, 5], 0.09090909091]
            }

def calc_band(value, bands, scores, feature):
    for index, band in enumerate(bands):
        if '<' in band:
            band_val = float(band.split("<")[1])
            if value < band_val:
                return scores[index]
        elif '>' in band:
            band_val = float(band.split(">")[1])
            if value >= band_val:
                return scores[index]
        elif '-' in band:
            left = float(band.split("-")[0])
            right = float(band.split("-")[1])
            if left <= value and value < right:
                return scores[index]
    print(f"No Band found for value {value}")
    print(feature)
        

def calc_points(value, feature):
    bands = features[feature][0]
    points = features[feature][1]
    weightage = features[feature][2]
    score = calc_band(value, bands, points, feature)
    return score * weightage

def calc_score(row):
    score = 0
    for feature in features.keys():
        score += calc_points(row[feature], feature)
    row['final_score'] = score
    return row

# Change this to config
scorecard_bands = {
    '5-7': ['Sell', 2],
    '7-10': ['Hold', 3],
    '10-15': ['Buy', 4],
    '15-18': ['Buy', 2],
    '>18': ['Buy', 3]
}

def create_flags(row):
    for key in scorecard_bands.keys():
        if '-' in key:
            m = key.split('-')
            left = float(m[0])
            right = float(m[1])
            if left <= row['final_score'] and row['final_score'] <= right:
                row['Flag'] = scorecard_bands[key][0]
        elif '>' in key:
            val = float(key.split('>')[1])
            if row['final_score'] > val:
                row['Flag'] = scorecard_bands[key][0]
    return row

def impute_column(data, column):
    data[column] = data[column].fillna(0)
    for index, row in data.iterrows():
        if row[column] == 0:
            temp = row[column]
            idx = index
            while temp == 0:
                temp = data.iloc[idx][column]
                idx = idx - 1
    return data

def create_scorecard_variables(data):
    data['rsi'] = rsiFunc(np.asarray(data['Close']))
    data = impute_column(data, 'rsi')
    data = count_highs(data, 'High', 14)
    data = count_highs(data, 'High', 7)
    data = count_highs(data, 'Low', 14)
    data = count_highs(data, 'Low', 7)
    data = calc_ratio_ema(data, 50, 200)
    data = calc_ratio_ema(data, 20, 50)
    data = calc_ratio_ema(data, 5, 20)
    data = calc_52wh_by_cmp(data)
    data = impute_column(data, 'Cmp_by_High52W')
    data = volume_growth(data, 7)
    data = open_vs_close(data, 7)
    data = data.apply(calc_score, axis=1)
    data = data.apply(create_flags, axis = 1)
    return data



