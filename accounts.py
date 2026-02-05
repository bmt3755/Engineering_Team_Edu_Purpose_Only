
class Account:
    def __init__(self, username: str, initial_deposit: float) -> None:
        self.username = username
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.portfolio = {}
        self.transactions = []

    def deposit(self, amount: float) -> None:
        self.balance += amount
        self.transactions.append(f'Deposit: ${amount}')

    def withdraw(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            self.transactions.append(f'Withdraw: ${amount}')
            return True
        return False

    def buy_shares(self, symbol: str, quantity: int) -> bool:
        price = get_share_price(symbol)
        total_cost = price * quantity
        if self.balance >= total_cost:
            self.balance -= total_cost
            if symbol in self.portfolio:
                self.portfolio[symbol] += quantity
            else:
                self.portfolio[symbol] = quantity
            self.transactions.append(f'Buy {quantity} of {symbol} at ${price} each')
            return True
        return False

    def sell_shares(self, symbol: str, quantity: int) -> bool:
        if symbol in self.portfolio and self.portfolio[symbol] >= quantity:
            price = get_share_price(symbol)
            total_revenue = price * quantity
            self.balance += total_revenue
            self.portfolio[symbol] -= quantity
            if self.portfolio[symbol] == 0:
                del self.portfolio[symbol]
            self.transactions.append(f'Sell {quantity} of {symbol} at ${price} each')
            return True
        return False

    def get_portfolio_value(self) -> float:
        total_value = 0.0
        for symbol, quantity in self.portfolio.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        return total_value

    def get_profit_or_loss(self) -> float:
        total_assets = self.balance + self.get_portfolio_value()
        return total_assets - self.initial_deposit

    def get_holdings(self) -> dict:
        return self.portfolio.copy()

    def get_transaction_history(self) -> list:
        return self.transactions.copy()

def get_share_price(symbol: str) -> float:
    test_prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0
    }
    return test_prices.get(symbol, 0.0)

# Example implementation with testing
def test_account_module():
    account = Account('user1', 1000)
    account.deposit(500)
    assert account.withdraw(300) == True
    assert account.withdraw(1500) == False
    assert account.buy_shares('AAPL', 2) == True
    assert account.buy_shares('TSLA', 1) == True
    assert account.sell_shares('AAPL', 1) == True
    assert account.sell_shares('TSLA', 2) == False
    print(account.get_holdings())
    print(account.get_portfolio_value())
    print(account.get_profit_or_loss())
    print(account.get_transaction_history())

test_account_module()
