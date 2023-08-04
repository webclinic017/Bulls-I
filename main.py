# This is the man program which will execute the program. BullsEye starts from here:
# Import libraries
import datetime
import yaml
from pya3 import *
from stock_selection import select_stocks
from execute import execute_actions
from mail import send_email
import pytz

def tuple_constructor(loader, node):
    # Convert the string representation of a tuple to a Python tuple
    return tuple(loader.construct_sequence(node))

# Register the custom constructor for PyYAML
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:seq', tuple_constructor)

# Reading config file
config_name='config.yml'
with open (config_name, 'r') as file:
    config=yaml.safe_load(file)

def login_aliceB():
    alice = Aliceblue(user_id=config['general_info']['alice_blue']['user_id'],api_key=config['general_info']['alice_blue']['api_key'])
    sessionid = alice.get_session_id() # Get Session ID
    if sessionid['stat'] != 'Ok':
        print("Please login in Alice Blue account...")
    else:
        print('Alice Blue Session Created!!!')
    return alice

def check_process_time(config):
    # Convert start_time and end_time strings to datetime objects in the 'Asia/Kolkata' timezone
    tz = pytz.timezone('Asia/Kolkata')

    start_time_str = config['general_info']['start_time']
    end_time_str = config['general_info']['end_time']

    start_time = datetime.strptime(start_time_str, "%H:%M:%S")
    end_time = datetime.strptime(end_time_str, "%H:%M:%S")

    start_time = tz.localize(start_time)
    end_time = tz.localize(end_time)

    # Get the current time in the 'Asia/Kolkata' timezone
    current_time = datetime.now(tz)

    # Compare the times
    if start_time <= current_time <= end_time:
        print("Current time is within the specified range.")
        return True
    else:
        print("Current time is outside the specified range.")
        return False

# Main Code
# One time initiation script to setup databases and other instances
def initiate():
    # This will run between the start time and end time of the day
    print("Process initiating....")
    stock_selection_time = config['general_info']['stock_selection_time']
    sender_email = config['general_info']['email']['sender_email']
    recipient_emails = config['general_info']['email']['recipients']
    # send_email(sender_email, recipient_emails, "Program initiated", "")
    # Select Stocks to trade upon and create a list with actions
    alice = login_aliceB()
    # Load data
    stock_selection_flag = 0
    execution_flag = 0
    # if check_process_time(config):
        # if stock_selection_time < current_time and stock_selection_flag == 0:
    print("Stock Selection process has begun....")
    action_table = select_stocks(config, alice, mode="LAST")
    print("Stock Selection process has ended!!!")
            # stock_selection_flag = 1
        # if stock_selection_flag == 1:
            # Execute calls
    print("Execution process has begun....")
    execute_actions(alice, action_table, config)
    print("Stock Selection process has ended!!!!")
            # execution_flag = 1
        # update database
        
        # Send Mails
        # send_mails()

initiate()