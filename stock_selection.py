# This file is used for selecting stocks
from pya3 import *
import datetime
import pandas as pd
import yaml
from feature_engineering import feature_engineering
from strategy import TradingStrategy
from db_ops import *

# def tuple_constructor(loader, node):
#     # Convert the string representation of a tuple to a Python tuple
#     return tuple(loader.construct_sequence(node))

# # Register the custom constructor for PyYAML
# yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:seq', tuple_constructor)

# # Reading config file
# config_name='config.yml'
# with open (config_name, 'r') as file:
#     config=yaml.safe_load(file)

def login_aliceB(config):
    alice = Aliceblue(user_id=config['general_info']['alice_blue']['user_id'],api_key=config['general_info']['alice_blue']['api_key'])
    print('Alice Blue Session Created!!!')
    print('Session ID: ', alice.get_session_id()) # Get Session ID
    return alice

def apply_strategies(stock_data,config):
    strategies = config['strategy']
    for key in strategies.keys():
        temp = TradingStrategy(key, conditions=strategies[key][0], action=strategies[key][1])
        stock_data = stock_data.apply(temp.create_strategy_flag, axis=1) # Later on change this to apply on last day's only
    return stock_data

def create_action_file(stock_data_with_flags, action_table, stock):
    stock_data_with_flags['Stock'] = stock
    # Use the 'insert' method to move the 'New_Stock' column to the first position
    stock_data_with_flags.insert(0, 'Stock', stock_data_with_flags.pop('Stock'))
    action_table = pd.concat([action_table, stock_data_with_flags])
    return action_table

def save_actions_file(action_table, mode):

    # Assuming you have your DataFrame 'action_table' ready

    # Get the current date in the format 'dd-mm-yyyy'
    current_date = datetime.datetime.now().strftime('%d-%m-%Y')

    current_time = datetime.datetime.now().strftime('%H-%M-%S')

    
    # Create the file name with the current date
    if mode == "ALL":
        file_name = f"Action_table-{current_date}.csv"
    elif mode == "LAST":
        file_name = f"Action_table-{current_date}-{current_time}.csv"

    # Save the DataFrame to CSV with the generated file name
    action_table.to_csv(file_name, index=False)
    print(f"Action file has been saved ({file_name})")


def select_stocks(config, alice = '', mode = None):
    if alice == '':
        alice = login_aliceB(config)
    stock_list = read_stock_list(config)
    action_table = pd.DataFrame()
    
    for stock in stock_list:
        try:
            stock_data = fetch_and_update_stock_data(stock, alice, mode) # OPTIMISE
        except Exception as e:
            print('fetch_and_update_stock_data not completed!!!')
            print(e)
        try:
            stock_data = feature_engineering(stock_data)
        except Exception as e:
            print('Error in feature_engineering!!!')
            print(e)
        try:
            stock_data_with_flags = apply_strategies(stock_data.iloc[-2:-1], config) # Just capture previous day stats
            # stock_data_with_flags = apply_strategies(stock_data) # On full data
        except Exception as e:
            print('apply_strategies not completed!!!')
            print(e)
        action_table = create_action_file(stock_data_with_flags, action_table, stock)
    save_actions_file(action_table, mode)
    return action_table