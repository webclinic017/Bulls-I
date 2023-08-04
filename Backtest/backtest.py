import yaml
import pandas as pd
import numpy as np

def tuple_constructor(loader, node):
    # Convert the string representation of a tuple to a Python tuple
    return tuple(loader.construct_sequence(node))

# Register the custom constructor for PyYAML
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:seq', tuple_constructor)

# Reading config file
config_name='config.yml'
with open (config_name, 'r') as file:
    config=yaml.safe_load(file)

class Backtest():
    def __init__(self, investment) -> None:
        self.investment = investment
        self.cash = investment
        self.current_holdings = []
        self.trades = []
        self.transactions = []
        self.performance = None
        self.total_profit = None
        self.no_of_trades = None
        pass

    def assign_quantity(self, subset, stock_pool):
        for index, row in subset.iterrows():
            subset.at[index, 'quantity'] = np.floor(stock_pool / row['Close'])
        return subset
        

    def allocate_quantities(self, subset):
        # Change this logic to config
        bin1 = subset.loc[(subset['final_score'] < 15) & (subset['final_score'] >= 10)]
        bin2 = subset.loc[(subset['final_score'] < 18) & (subset['final_score'] >= 15)]
        bin3 = subset.loc[(subset['final_score'] >= 18)]
        bins = [bin1, bin2, bin3]
        bucket_amounts_division = config['scorecard']['strategy']['amounts'][-3:]
        for i in range(3):
            if not bins[i].empty:
                # Decide amount for this bin
                bin_amount = self.cash * bucket_amounts_division[i]
                # Decide Stock pool
                num_stocks = bins[i]['Stock'].nunique()
                stock_pool = bin_amount / num_stocks
                bins[i] = self.assign_quantity(bins[i], stock_pool)
        subset_with_quantity = pd.concat(bins)
        return subset_with_quantity
    
    def get_holding_data(self, stockname):
        for stock in self.current_holdings:
            if stock['Name'] == stockname:
                return stock['Qty'], stock['BuyPrice']
    
    def check_current_holdings(self, row):
        idx = 0
        for stock in self.current_holdings:
            if stock['Name'] == row['Stock']:
                return True, idx 
            idx += 1
        return False, None
    
    def buy(self, row):
        # Check if it is already in holdings
        flag, idx = self.check_current_holdings(row)
        
        if not flag and row['quantity'] != 0:
            amount_needed = row['Close'] * row['quantity']
            if amount_needed < self.cash and row['Stock'] not in self.current_holdings:
                self.cash -= amount_needed
                self.current_holdings.append({'Name': row['Stock'],
                                            'Qty': row['quantity'],
                                            'BuyPrice': row['Close']})
                self.transactions.append({'Action': 'Buy',
                                        'Name': row['Stock'],
                                        'Price': row['Close'],
                                        'Qty': row['quantity']})
        
    def sell(self, row):
        flag, idx = self.check_current_holdings(row)
        if flag:
            qty, buy_price = self.get_holding_data(row['Stock'])
            sell_price = row['Close']
            amount_received = sell_price * qty
            self.cash += amount_received
            self.transactions.append({'Action': 'Sell',
                                'Name': row['Stock'],
                                'Price': row['Close'],
                                'Qty': qty})
        
            self.trades.append({
                'Stock': row['Stock'],
                'BuyPrice': buy_price,
                'SellPrice': sell_price,
                'Qty': qty,
                'Gain': (sell_price-buy_price) * qty,
                'Perc': (sell_price - buy_price) / buy_price,
                'score': row['final_score']
            })
            self.current_holdings.pop(idx)

    def get_profit(self):
        profit = 0
        for trade in self.trades:
            profit += trade['Gain']
        return profit
    
    def decode_bands(self):
        bands = config['scorecard']['strategy']['score_bands']
        bands_decoded = []
        for band in bands:
            if '-' in band:
                m = band.split('-')
                left = float(m[0])
                right = float(m[1])
                bands_decoded.append((left, right, band))
            elif '>' in band:
                val = float(band.split('>')[1])
                bands_decoded.append((val, 999, band))
        return bands_decoded
    
    def assign_band_based_on_score(self, score, bands):
        for band in bands:
            if band[0] < score and score < band[1]:
                return band[2]
        print(f"No band found for score {score}")

    def assign_bands(self, data):
        bands = self.decode_bands()
        for index, row in data.iterrows():
            data.at[index, 'score_band'] = self.assign_band_based_on_score(row['scores'], bands)
        return data
    
    def get_scorecard_performance(self):
        # Rollup profits based on the score bands
        investments = []
        scores = []
        profits = []
        for trade in self.trades:
            investments.append(trade['BuyPrice'] * trade['Qty'])
            scores.append(trade['score'])
            profits.append(trade['Gain'])

        data = pd.DataFrame({
            "scores": scores,
            "profits": profits,
            "investments": investments
        })
        if not data.empty:
            data = self.assign_bands(data)
            data = data.groupby('score_band').agg({
                "profits": sum,
                "investments": sum
            })

            data['percentage'] = data['profits'] / data['investments'] * 100
            return data
        else:
            print("Action table had zero Sell flag")
        

    def get_results(self):
        # Total no of trades taken
        no_of_trades = len(self.trades)
        self.no_of_trades = no_of_trades
        # Number of trades taken for each stock
        # Profit/Loss amount and percentage
        profit = self.get_profit()
        self.total_profit = profit
        # Score bands vs Profits
        scorecard_performance = self.get_scorecard_performance()
        self.performance = scorecard_performance
        # Best Stock vs Worst Stock

    def fit(self, action_table):
        days = action_table['Date'].unique()
        for day in days:
            subset = action_table.loc[action_table['Date'] == day]
            subset = self.allocate_quantities(subset)
    
            for index, row in subset.iterrows():
                if row['Flag'] == 'Buy':
                    self.buy(row)
                
                elif row['Flag'] == 'Sell':
                    self.sell(row)
        try:
            self.get_results()
        except KeyError:
            print("No SELL FLAG FOUND")
        print("Backtesting has been completed!")


        



