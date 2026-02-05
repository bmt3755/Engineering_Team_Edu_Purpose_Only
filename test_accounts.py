import unittest
from unittest.mock import patch
import accounts


class TestAccount(unittest.TestCase):
    def setUp(self):
        """Set up a fresh Account instance before each test."""
        self.account = accounts.Account('testuser', 1000.0)
    
    def test_initialization(self):
        """Test that Account initializes with correct attributes."""
        self.assertEqual(self.account.username, 'testuser')
        self.assertEqual(self.account.initial_deposit, 1000.0)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(self.account.transactions, [])
    
    def test_deposit(self):
        """Test deposit method increases balance and records transaction."""
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertIn('Deposit: $500.0', self.account.transactions)
    
    def test_withdraw_success(self):
        """Test successful withdrawal."""
        result = self.account.withdraw(300.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 700.0)
        self.assertIn('Withdraw: $300.0', self.account.transactions)
    
    def test_withdraw_failure(self):
        """Test withdrawal with insufficient balance."""
        result = self.account.withdraw(1500.0)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(len(self.account.transactions), 0)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_success(self, mock_get_price):
        """Test buying shares with sufficient balance."""
        mock_get_price.return_value = 150.0  # AAPL price
        result = self.account.buy_shares('AAPL', 2)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 1000.0 - (150.0 * 2))  # 700.0
        self.assertEqual(self.account.portfolio, {'AAPL': 2})
        self.assertIn('Buy 2 of AAPL at $150.0 each', self.account.transactions)
    
    @patch('accounts.get_share_price')
    def test_buy_shares_failure(self, mock_get_price):
        """Test buying shares with insufficient balance."""
        mock_get_price.return_value = 2800.0  # GOOGL price
        result = self.account.buy_shares('GOOGL', 1)
        self.assertFalse(result)
        self.assertEqual(self.account.balance, 1000.0)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(len(self.account.transactions), 0)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_success(self, mock_get_price):
        """Test selling shares when holding enough."""
        mock_get_price.return_value = 150.0
        self.account.buy_shares('AAPL', 3)
        # Reset mock to ensure sell uses current price
        mock_get_price.return_value = 160.0
        result = self.account.sell_shares('AAPL', 2)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 1000.0 - (150.0 * 3) + (160.0 * 2))  # 1000 - 450 + 320 = 870
        self.assertEqual(self.account.portfolio, {'AAPL': 1})
        self.assertIn('Sell 2 of AAPL at $160.0 each', self.account.transactions)
    
    @patch('accounts.get_share_price')
    def test_sell_shares_failure_insufficient_quantity(self, mock_get_price):
        """Test selling more shares than held."""
        mock_get_price.return_value = 150.0
        self.account.buy_shares('AAPL', 1)
        result = self.account.sell_shares('AAPL', 2)
        self.assertFalse(result)
        self.assertEqual(self.account.portfolio, {'AAPL': 1})
        self.assertEqual(len(self.account.transactions), 1)  # Only buy transaction
    
    @patch('accounts.get_share_price')
    def test_sell_shares_failure_no_symbol(self, mock_get_price):
        """Test selling shares of a symbol not in portfolio."""
        mock_get_price.return_value = 150.0
        result = self.account.sell_shares('TSLA', 1)
        self.assertFalse(result)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(len(self.account.transactions), 0)
    
    @patch('accounts.get_share_price')
    def test_get_portfolio_value(self, mock_get_price):
        """Test portfolio value calculation."""
        mock_get_price.side_effect = lambda sym: {'AAPL': 150.0, 'TSLA': 700.0}.get(sym, 0.0)
        self.account.buy_shares('AAPL', 2)
        self.account.buy_shares('TSLA', 1)
        value = self.account.get_portfolio_value()
        expected = (150.0 * 2) + (700.0 * 1)
        self.assertEqual(value, expected)
    
    @patch('accounts.get_share_price')
    def test_get_profit_or_loss(self, mock_get_price):
        """Test profit/loss calculation."""
        mock_get_price.return_value = 150.0
        self.account.buy_shares('AAPL', 2)  # Cost 300, balance 700
        # Mock price for portfolio value
        mock_get_price.return_value = 200.0  # Price increased
        profit = self.account.get_profit_or_loss()
        # Total assets: balance 700 + portfolio (200*2=400) = 1100, initial deposit 1000, profit 100
        self.assertEqual(profit, 100.0)
    
    def test_get_holdings(self):
        """Test get_holdings returns a copy of portfolio."""
        with patch('accounts.get_share_price', return_value=150.0):
            self.account.buy_shares('AAPL', 2)
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {'AAPL': 2})
        # Ensure it's a copy, not the same object
        self.assertIsNot(holdings, self.account.portfolio)
    
    def test_get_transaction_history(self):
        """Test get_transaction_history returns a copy of transactions."""
        self.account.deposit(500.0)
        history = self.account.get_transaction_history()
        self.assertEqual(history, ['Deposit: $500.0'])
        self.assertIsNot(history, self.account.transactions)


class TestGetSharePrice(unittest.TestCase):
    def test_get_share_price_existing(self):
        """Test get_share_price returns correct price for known symbols."""
        self.assertEqual(accounts.get_share_price('AAPL'), 150.0)
        self.assertEqual(accounts.get_share_price('TSLA'), 700.0)
        self.assertEqual(accounts.get_share_price('GOOGL'), 2800.0)
    
    def test_get_share_price_non_existing(self):
        """Test get_share_price returns 0.0 for unknown symbol."""
        self.assertEqual(accounts.get_share_price('UNKNOWN'), 0.0)


if __name__ == '__main__':
    unittest.main()
