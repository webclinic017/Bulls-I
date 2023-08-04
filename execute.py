from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pya3 import *
import yaml

# Reading config file
config_name='config.yml'
with open (config_name, 'r') as file:
    config=yaml.safe_load(file)


# EXECUTE TRADE ON STOCK BROKER
def buy_stock(alice, quantity, symbol):
    # TransactionType.Buy, OrderType.Market, ProductType.Delivery

    print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%1%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    res = alice.place_order(transaction_type = TransactionType.Buy,
                        instrument = alice.get_instrument_by_symbol('NSE', symbol),
                        quantity = quantity,
                        order_type = OrderType.Market,
                        product_type = ProductType.Delivery,
                        price = 0.0,
                        trigger_price = None,
                        stop_loss = None,
                        square_off = None,
                        trailing_sl = None,
                        is_amo = False,
                        order_tag=symbol + ' ' + str(quantity) + 'BUY')
    return res

def sell_stock(alice, quantity, symbol):
    # TransactionType.Buy, OrderType.Market, ProductType.Delivery

    print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%1%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    res = alice.place_order(transaction_type = TransactionType.Sell,
                        instrument = alice.get_instrument_by_symbol('NSE', symbol),
                        quantity = quantity,
                        order_type = OrderType.Market,
                        product_type = ProductType.Delivery,
                        price = 0.0,
                        trigger_price = None,
                        stop_loss = None,
                        square_off = None,
                        trailing_sl = None,
                        is_amo = False,
                        order_tag=symbol + ' ' + str(quantity) + 'SELL')
    return res


# Now we have stocks and actions for that day
# It may be possible that the action 'buy' may have come from one strategy for a stock, and another same action for another stock from different strategy
# We want to track which strategy led to that action for a stock, time of transaction, amount invested and so on

# STEPS:
# 1. Read the actions file of that day
# 2. Allocate quantity to the selected stocks
# 3. Execute actions as directed (Intraday and Daytrading modules should be separate)
# 4. Document details related to that transaction

def read_action_file():
    # Get the current date in the format 'dd-mm-yyyy'
    current_date = datetime.now()
    day_before = timedelta(days=2)
    dt = current_date - day_before
    # Format the date as a string
    dt = dt.strftime('%d-%m-%Y')

    # Create the file name with the current date
    file_name = f"Action_table-{dt}.csv"

    # Save the DataFrame to CSV with the generated file name
    action_table = pd.read_csv(file_name)

    return action_table

def calc_stock_preference(df):
    df = df.sort_values(by='rsi_avg_chg', ascending=False) # Just for example purposes # Need to consult
    return df

def decide_units_buy(df, cash):
    final = {}
    # This is where we will decide which stock should be given more preference
    df = calc_stock_preference(df)
    stocks = np.asarray(df['Stock'])
    stockPrices = np.asarray(df['Close'])
    idx = 0
    lastIdx = df.shape[0]
    while True:
        if stocks[idx] in final.keys():
            if stockPrices[idx] < cash:
                final[stocks[idx]] += 1
                cash -= stockPrices[idx]
            else:
                break
        else:
            if stockPrices[idx] < cash:
                final[stocks[idx]] = 1
                cash -= stockPrices[idx]
            else:
                final[stocks[idx]] = 0
        idx += 1
        if idx == lastIdx:
            idx = 0
    return final

def get_current_holdings(alice):
    holdings = alice.get_holding_positions()
    myholdings = {
        'stock': [],
        'units': [],
        'price': [],
        'LTP': []
    }
    stocks = stocks['Stock'].values
    for share in holdings['HoldingVal']:
        if share["Bsetsym"] in stocks:
            myholdings['stock'].append(share["Bsetsym"])
            myholdings['units'].append(share["authQty"])
            myholdings['price'].append(share["Price"])
            myholdings['LTP'].append(share["Ltp"])
    myholdings = pd.DataFrame(myholdings)
    return myholdings

def decide_units_sell(stocks, alice):
    holdings = get_current_holdings(alice)
    final = {}
    stocks = holdings['Stock'].values
    units = holdings['units'].values
    for i in range(len(stocks)):
        final[stocks[i]] = units[i]
    return final

def allocate_funds(funds_perc, alice):
    cash = float(alice.get_balance()[0]['net'])
    cash = cash * funds_perc / 100
    return cash

def execute(order_list, action, alice):
    for stock in order_list.keys():
        quantity = order_list[stock]
        if quantity != 0:
            if action == 'BUY':
                # res = buy_stock(alice, quantity, stock)
                print(f"{quantity} of {stock} bought!")
                # place_stop_loss #IMPORTANT
                # Send notification

            if action == 'SELL':
                # res = sell_stock(alice, quantity, stock)
                print(f"{quantity} of {stock} sold!")
    
    # Post Analytics module
    

    # return res
    return

def execute_actions(alice, action_table = pd.DataFrame(), config = None):
    if action_table.empty:
        action_table = read_action_file()
    else:
        # For each strategy
        strategies = config['strategy'].keys()
        # Strategy lifecycle starts from here
        for strategy in strategies: 
            action = config['strategy'][strategy][1]
            # allocate funds
            funds = allocate_funds(funds_perc=config['strategy'][strategy][2], alice=alice)
            # For each stock selected under each strategy, allocate quantity
            if strategy in action_table.columns:
                selected_stocks = action_table.loc[action_table[strategy] == action]
                if action == "BUY":
                    order_list = decide_units_buy(selected_stocks, funds)
                if action == "SELL":
                    order_list = decide_units_sell(selected_stocks, alice)
                # Execute order on Exchange
                print(f"({strategy}): Order list has been generated...")
                print(order_list)
                res = execute(order_list, action, alice)
        

# def login_aliceB():
#     alice = Aliceblue(user_id=config['general_info']['alice_blue']['user_id'],api_key=config['general_info']['alice_blue']['api_key'])
#     print('Alice Blue Session Created!!!')
#     print('Session ID: ', alice.get_session_id()) # Get Session ID
#     return alice

# alice = login_aliceB()
# execute_actions(alice)
