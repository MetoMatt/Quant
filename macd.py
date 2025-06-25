import yfinance as yf  # Import yfinance for downloading data # 導入yfinance用於下載數據
import pandas as pd  # Import pandas for data manipulation # 導入pandas用於數據處理
import numpy as np  # Import numpy for numerical operations # 導入numpy用於數值運算
import talib  # Import TA-Lib for technical indicators # 導入TA-Lib用於技術指標

# Download historical data for BTC-USD from Yahoo Finance # 從Yahoo財經下載BTC-USD的歷史數據
data = yf.download('BTC-USD', start='2022-01-01', end='2023-01-01', interval='1d')

# Check if data is valid # 檢查數據是否有效
if data is None or data.empty:
    print('No data downloaded. Please check the ticker or date range.')  # 沒有下載到數據，請檢查代碼或日期範圍
    exit()

# Drop missing values # 去除缺失值
data = data.dropna()

# Prepare numpy arrays for TA-Lib # 準備TA-Lib需要的numpy數組
close_array = data['Close'].to_numpy().flatten()  # Closing prices # 收盤價
high_array = data['High'].to_numpy().flatten()    # High prices # 最高價
low_array = data['Low'].to_numpy().flatten()      # Low prices # 最低價

# Calculate MACD indicator step by step # 分步計算MACD指標
macd_result = talib.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)  # Get MACD result # 獲取MACD結果
macd = macd_result[0]  # MACD line # MACD線
macdsignal = macd_result[1]  # Signal line # 信號線
macdhist = macd_result[2]  # MACD histogram # MACD柱狀圖

# Calculate ATR (Average True Range) for stop loss step by step # 分步計算ATR用於止損
atr = talib.ATR(high_array, low_array, close_array, timeperiod=14)  # ATR value # ATR值

# Find the first index where all indicators are valid (not NaN) # 找到所有指標都有效的第一個索引
start = max(
    np.where(np.isnan(macd))[0].max() if np.isnan(macd).any() else 0,
    np.where(np.isnan(macdsignal))[0].max() if np.isnan(macdsignal).any() else 0,
    np.where(np.isnan(atr))[0].max() if np.isnan(atr).any() else 0,
) + 1

# Initialize variables for backtest # 初始化回測用的變量
position = 0  # 0 means no position, 1 means holding # 0表示沒有持倉，1表示持有
buy_price = 0  # Record the buy price # 記錄買入價格
stop_loss = 0  # Record the stop loss price # 記錄止損價格
trades = []  # List to store trade records # 用於存儲交易記錄的列表

# Loop through the data to simulate trading # 遍歷數據以模擬交易
for i in range(start, len(data)):
    # Gold cross: MACD crosses above signal line # 金叉：MACD上穿信號線
    if macd[i-1] < macdsignal[i-1] and macd[i] > macdsignal[i] and position == 0:
        position = 1  # Enter position # 進場
        buy_price = close_array[i]  # Set buy price # 設置買入價格
        stop_loss = buy_price - 2.5 * atr[i]  # Set stop loss at 2.5x ATR below buy # 設置止損價為買入價下方2.5倍ATR
        trades.append({'type': 'buy', 'date': data.index[i], 'price': buy_price, 'stop_loss': stop_loss})  # Record buy # 記錄買入
    # Dead cross: MACD crosses below signal line # 死叉：MACD下穿信號線
    elif macd[i-1] > macdsignal[i-1] and macd[i] < macdsignal[i] and position == 1:
        position = 0  # Exit position # 平倉
        sell_price = close_array[i]  # Set sell price # 設置賣出價格
        trades.append({'type': 'sell', 'date': data.index[i], 'price': sell_price})  # Record sell # 記錄賣出
    # Stop loss: price falls below stop loss # 止損：價格跌破止損價
    elif position == 1 and close_array[i] < stop_loss:
        position = 0  # Exit position # 平倉
        sell_price = close_array[i]  # Set sell price # 設置賣出價格
        trades.append({'type': 'stop_loss', 'date': data.index[i], 'price': sell_price})  # Record stop loss # 記錄止損

# Print all trades # 輸出所有交易
for trade in trades:
    print(trade)
