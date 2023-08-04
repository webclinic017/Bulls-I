class User:
    def __init__(self, user_id, username, email, password):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password


class Admin(User):
    def __init__(self, user_id, username, email, password):
        super().__init__(user_id, username, email, password)


class Investor(User):
    def __init__(self, user_id, username, email, password):
        super().__init__(user_id, username, email, password)
        self.investments = []  # List to store information about investments
        self.withdrawals = []  # List to store information about withdrawals
        self.available_funds = 0

    def calculate_profit(self, total_investment, platform_profit):
        # Sum of all the transactions done by the user
        total_investment_by_user = sum(investment["amount"] for investment in self.investments)
        # Calculate user investment percentage
        user_percentage = total_investment_by_user / total_investment
        # Calculate user profit
        user_profit = user_percentage * platform_profit
        return user_profit


class DataAnalyst(User):
    def __init__(self, user_id, username, email, password):
        super().__init__(user_id, username, email, password)
        self.analytical_reports = []  # List to store analytical reports


class BullsEyeUser:
    def __init__(self, platform_profit_percentage=1.0):
        self.platform_profit_percentage = platform_profit_percentage
        self.users = {}  # Dictionary to store users (user_id: User object)
        self.total_investment = 0.0

    def add_user(self, user):
        self.users[user.user_id] = user

    def remove_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def get_user_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user

    def get_all_investors(self):
        investors = [user for user in self.users.values() if isinstance(user, Investor)]
        return investors

    def get_all_data_analysts(self):
        data_analysts = [user for user in self.users.values() if isinstance(user, DataAnalyst)]
        return data_analysts

    def get_total_investment(self):
        return self.total_investment

    def update_total_investment(self, amount):
        self.total_investment += amount

    def calculate_profit_for_all_investors(self):
        total_profit = 0.0
        for investor in self.get_all_investors():
            profit = investor.calculate_profit(self.total_investment, self.platform_profit_percentage)
            total_profit += profit
        return total_profit
