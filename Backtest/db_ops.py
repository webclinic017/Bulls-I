import datetime
import yfinance as yf
import pytz
import pandas as pd

def write(tablename, data):
    pass

def read(tablename):
    pass

def update(tablename, data, id):
    pass

def read_stock_list(config):
    stock_list = pd.read_csv(config['general_info']['stock_list_path'])
    stock_list = stock_list['Symbol'].values
    return stock_list

# FETCH DATA FROM YFINANCE
def fetchData(tickerSymbol):

    #get data on this ticker
    tickerData = yf.Ticker(tickerSymbol)
    
    # Get today's date
    today = datetime.date.today()

    # Format the date as "YYYY-M-D"
    formatted_date = today.strftime("%Y-%m-%d")

    #get the historical prices for this ticker
    stock = tickerData.history(period='1d', start='2000-2-1', end=formatted_date)
    stock.reset_index(inplace=True)
    return stock

def fetch_alice_blue_data(alice, index, stockName, days):
    instrument = alice.get_instrument_by_symbol(index, stockName)
    from_datetime = datetime.datetime.now() - datetime.timedelta(days)     # From last & days
    to_datetime = datetime.datetime.now()                                    # To now
    interval = "D"     # ["1", "D"]
    indices = False    # For Getting index data
    hist_data = alice.get_historical(instrument, from_datetime, to_datetime, interval, indices)

    hist_data['datetime'] = pd.to_datetime(hist_data['datetime'])
    hist_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    hist_data['Date'] = hist_data['Date'].dt.tz_localize(pytz.timezone('Asia/Kolkata'))
    return hist_data

def fetchAdditionalData(sorted_stock, index, stockName, alice):
    hist_data = fetch_alice_blue_data(alice, index, stockName, days=1400)
    last_index = sorted_stock.shape[0]
    date1 = sorted_stock['Date'][last_index - 1]
    
    start_date_index = hist_data.loc[hist_data['Date'] == date1].index + 1
    if start_date_index != hist_data.shape[0]:
        recent_data = hist_data.iloc[start_date_index,:]
        recent_data = recent_data.drop(recent_data.loc[recent_data['Volume'] == 0].index)

        if recent_data.shape[0] != 0:
            sorted_stock = pd.concat([sorted_stock, recent_data]).reset_index(drop = True)
    return sorted_stock
    
def fetch_and_update_stock_data(stock, alice, mode):
    # if data already present with us, then update that ## WRITE
    # if data not present with us, then create it
    # DATA PREPARATION
    # if mode == "ALL":
    data = fetchData(stock + ".NS") # Accepts .NS names
    data = fetchAdditionalData(data, "NSE", stock, alice)
    # if mode == "LAST":
    #     data = fetch_alice_blue_data(alice, "NSE", stock, 1)
    return data