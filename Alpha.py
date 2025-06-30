import yfinance as yf
import pandas as pd
import numpy as np
import talib
import seaborn as sns
import matplotlib.pyplot as plt
import backtesting as bt

window = 7

btc = yf.download('BTC-USD', start='2022-01-01', end='2023-01-01', interval='1d')


btc = btc.dropna()
btc['Return_7d'] = btc['Close'] / btc['Close'].shift(window) - 1  #Return in 7 days  # now over future?? # why minus 1?
btc['Volatility_7d'] = btc['Close'].rolling(window).std()         #Volatility in 7 days  #7天前？
btc['Alpha'] = btc['Return_7d'] / btc['Volatility_7d']          #Alpha = Return / Volatility
    
plt.figure()
sns.histplot(btc['Alpha'].dropna(), bins=50, kde=True)
plt.title('Alpha Distribution')
plt.show()

btc['AlphaRank'] = pd.qcut(btc['Alpha'], 5, labels=False) # 5 groups of Alpha
btc['Future_Return'] = btc['Close'].shift(-3) / btc['Close'] - 1
plt.figure()
btc.groupby('AlphaRank')['Future_Return'].mean().plot(kind='bar')
plt.title('Future Return(3 days) by Alpha Rank')
plt.xlabel('Alpha Rank')
plt.ylabel('Future Return')
plt.show()





