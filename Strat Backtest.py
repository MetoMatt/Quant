import pandas as pd
import numpy as np
import talib
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load the filtered data
# Use the correct datetime column from the CSV ('Date')
data_path = '/Users/metomatt/Documents/vscode/data/Binance_ADABTC_2025_minute.csv'
# Read the CSV, parse 'Date' as datetime, and set as index
data = pd.read_csv(data_path, parse_dates=['Date'], index_col='Date')

# Select and rename columns for backtesting
# We'll use Open, High, Low, Close, and Volume ADA as the main columns
data = data[['Open', 'High', 'Low', 'Close', 'Volume ADA']]
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Define a flexible strategy class
class BollingerBandBreakoutShort(Strategy):
    window = 21
    num_std = 2.7
    take_profit = 0.05  # 5%
    stop_loss = 0.03    # 3%

    def init(self):
        # Calculate Bollinger Bands using TA-Lib
        self.upper_band, self.middle_band, self.lower_band = self.I(
            talib.BBANDS, self.data.Close, self.window, self.num_std, self.num_std)

    def next(self):
        # Only start trading after enough data for the window
        if len(self.data) < self.window:
            return
        # Check for breakout below lower band and no open position
        if self.data.Close[-1] < self.lower_band[-1] and not self.position:
            self.sell(sl=self.data.Close[-1] * (1 + self.stop_loss),
                      tp=self.data.Close[-1] * (1 - self.take_profit))

# Create and configure the backtest
bt = Backtest(data, BollingerBandBreakoutShort, cash=100000, commission=0.002)

# Run the backtest with default parameters and print the results
stats_default = bt.run()
print("Default Parameters Results:")
print(stats_default)

# Now perform the optimization
# Note: The constraint lambda uses dictionary keys for parameters
optimization_results = bt.optimize(
    window=range(10, 20, 5),
    num_std=[round(i, 1) for i in np.arange(1.5, 3.5, 0.1)],
    take_profit=[i / 100 for i in range(1, 7, 1)],  # Optimize TP from 1% to 6%
    stop_loss=[i / 100 for i in range(1, 7, 1)],    # Optimize SL from 1% to 6%
    maximize='Equity Final [$]',
    constraint=lambda param: param['window'] > 0 and param['num_std'] > 0
)

# Print the optimization results
print("\nOptimization Results:")
print(optimization_results)

# Print the best parameters in a version-agnostic way
print("\nBest Parameters:")
if isinstance(optimization_results, dict):
    # Newer versions: optimization_results is a dict of stats and parameters
    for key in ['window', 'num_std', 'take_profit', 'stop_loss']:
        print(f"{key}: {optimization_results.get(key)}")
# Handle tuple return type: (stats, strategy_instance)
elif isinstance(optimization_results, tuple) and len(optimization_results) == 2:
    stats, strat = optimization_results
    print(f"window: {getattr(strat, 'window', None)}")
    print(f"num_std: {getattr(strat, 'num_std', None)}")
    print(f"take_profit: {getattr(strat, 'take_profit', None)}")
    print(f"stop_loss: {getattr(strat, 'stop_loss', None)}")
else:
    print("Could not determine best parameters format. Please check the optimization_results output above.")

# Print only the best parameters from the stats Series
print("\nBest Parameters (from stats):")
print("Check the optimization results above for the best parameters.")
print("They appear as rows in the stats output with values for window, num_std, take_profit, and stop_loss.")