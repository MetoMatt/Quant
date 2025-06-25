import yfinance as yf
import pandas as pd
import numpy as np
import talib
import seaborn as sns
import matplotlib.pyplot as plt

window = 7

btc = yf.download('BTC-USD', start='2022-01-01', end='2023-01-01', interval='1d')

if btc is not None and not btc.empty:
    btc = btc.dropna()
    btc['Return_7d'] = btc['Close'] / btc['Close'].shift(window) - 1  #Return in 7 days
    btc['Volatility_7d'] = btc['Close'].rolling(window).std()
    btc['Alpha'] = btc['Return_7d'] - btc['Volatility_7d']
    sns.histplot(btc['Alpha'].dropna(), bins=50, kde=True)
    plt.title('Alpha Distribution')
    plt.show()





else:
    print("Failed to download data")