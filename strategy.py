class TradingStrategy:
    def __init__(self, name, conditions, action, funds = None):
        self.name = name
        self.conditions = conditions  # List of tuples (indicator_name, operator, threshold)
        self.action = action  # 'BUY' or 'SELL'
        self.funds = funds

    def create_strategy_flag(self, data):
        flag = 1
        for condition in self.conditions:
            if condition[1] == "<":
                if data[condition[0]] < condition[2]:
                    continue
                else:
                    flag = 0
            if condition[1] == ">":
                if data[condition[0]] > condition[2]:
                    continue
                else:
                    flag = 0
            if condition[1] == "=":
                if data[condition[0]] == condition[2]:
                    continue
                else:
                    flag = 0
        if flag == 1:
            data[self.name] = self.action
        return data



