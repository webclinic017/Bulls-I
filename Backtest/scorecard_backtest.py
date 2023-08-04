import pandas as pd
import numpy as np
import yaml
from db_ops import *
from pya3 import *
from scorecard import *
from Backtest.backtest import *

def tuple_constructor(loader, node):
    # Convert the string representation of a tuple to a Python tuple
    return tuple(loader.construct_sequence(node))

# Register the custom constructor for PyYAML
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:seq', tuple_constructor)

# Reading config file
config_name='config.yml'
with open (config_name, 'r') as file:
    config=yaml.safe_load(file)

# Here we want to backtest the scorecard model. For backtesting we would need to perform these steps:
# 1. Prepare data of all the stocks present in the list.
# 2. Once the data is prepared, decide a time period for which we would like to take trades
# 3. Create an action list for that day
# 4. Take trades as per the strategy
# 5. Calculate profit and other relevant metrics

def login_aliceB(config):
    alice = Aliceblue(user_id=config['general_info']['alice_blue']['user_id'],api_key=config['general_info']['alice_blue']['api_key'])
    print('Alice Blue Session Created!!!')
    print('Session ID: ', alice.get_session_id()) # Get Session ID
    return alice

def read_stock_list(config):
    stock_list = pd.read_csv(config['general_info']['stock_list_path'])
    stock_list = stock_list['Symbol'].values
    return stock_list

def main():
    alice = login_aliceB(config)
    stock_list = read_stock_list(config)
    action_table = pd.DataFrame()
    count = 0
    for stock in stock_list:
        count += 1
        print(stock)
        try:
            stock_data = fetch_and_update_stock_data(stock, alice, 'ALL') # OPTIMISE
        except Exception as e:
            print('fetch_and_update_stock_data not completed!!!')
            print(e)

        # try:
        data = create_scorecard_variables(stock_data)
        # except:
        #     print("Variable creation failed!!!")
        #     print(stock)

        # Assign the Series to a new column in the DataFrame
        data['New_Stock'] = stock

        # Use the 'insert' method to move the 'New_Stock' column to the first position
        data.insert(0, 'Stock', data.pop('New_Stock'))
        
        # Data Control
        num_of_rows = 500
        data = data.iloc[-num_of_rows:]

        # Append it to the master table
        action_table = pd.concat([action_table, data])
        if count == 10:
            break
    action_table.to_csv('Backtest_action_tables.csv')
    # Execute Strategy
    # investment = config['backtest']['investment']
    # backtest = Backtest(investment=investment)
    # backtest.fit(action_table)