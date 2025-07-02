import pandas as pd
import numpy as np
import talib
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt

# Load the filtered data
# Use the correct datetime column from the CSV ('Date')
data_path = '/Users/metomatt/Documents/vscode/data/Binance_ADABTC_2025_minute.csv'
# Read the CSV, parse 'Date' as datetime, and set as index
data = pd.read_csv(data_path, parse_dates=['Date'], index_col='Date')

# Select and rename columns for backtesting
# We'll use Open, High, Low, Close, and Volume ADA as the main columns
data = data[['Open', 'High', 'Low', 'Close', 'Volume ADA']]
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# Define a MACD strategy class
class MACDStrategy(Strategy):
    fastperiod = 12
    slowperiod = 26
    signalperiod = 9
    atr_period = 14
    atr_mult = 3

    def init(self):
        # Calculate MACD using TA-Lib
        self.macd, self.macdsignal, self.macdhist = self.I(
            talib.MACD, self.data.Close, self.fastperiod, self.slowperiod, self.signalperiod)
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.signal_records = []  # Use a custom attribute for buy/sell records

    def next(self):
        # Only start trading after enough data for indicators
        if len(self.data) < max(self.slowperiod, self.atr_period):
            return
        price = self.data.Close[-1]
        atr = self.atr[-1]
        # Golden cross: MACD crosses above signal
        if crossover(self.macd, self.macdsignal) and not self.position:
            sl = price - self.atr_mult * atr
            self.buy(sl=sl)
            self.signal_records.append({'type': 'buy', 'index': self.data.index[-1], 'price': price, 'sl': sl})
        # Dead cross: MACD crosses below signal
        elif crossover(self.macdsignal, self.macd) and self.position:
            self.position.close()
            self.signal_records.append({'type': 'sell', 'index': self.data.index[-1], 'price': price})

# Create and configure the backtest
bt = Backtest(data, MACDStrategy, cash=100000, commission=0.002)

# Run the backtest with default parameters and print the results
stats_default = bt.run()
print("Default Parameters Results:")
print(stats_default)

# Output buy/sell records for later visualization
# Get the strategy instance from the backtest results
if isinstance(stats_default, tuple) and len(stats_default) == 2:
    _, strat_instance = stats_default
    records = getattr(strat_instance, 'signal_records', None)
else:
    records = getattr(MACDStrategy, 'signal_records', None)
if records is not None:
    trades_df = pd.DataFrame(records)
    print("\nBuy/Sell Records:")
    # Print colored table using rich
    console = Console(force_terminal=True)
    table = Table(title="Buy/Sell Records")
    for col in trades_df.columns:
        table.add_column(str(col))
    for _, row in trades_df.iterrows():
        style = "green" if row['type'] == 'buy' else "red"
        table.add_row(*[str(x) for x in row], style=style)
    console.print(table)
    # Plot with matplotlib
    plt.figure(figsize=(14, 6))
    plt.plot(data.index, data['Close'], label='Close', color='blue')
    if not trades_df.empty:
        buy_signals = trades_df[trades_df['type'] == 'buy']
        sell_signals = trades_df[trades_df['type'] == 'sell']
        plt.scatter(buy_signals['index'], buy_signals['price'], marker='^', color='green', label='Buy', s=100, zorder=5)
        plt.scatter(sell_signals['index'], sell_signals['price'], marker='v', color='red', label='Sell', s=100, zorder=5)
    plt.title('MACD Strategy Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

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

console = Console(force_terminal=True)
console.print("[green]This should be green[/green] [red]and this should be red[/red]")