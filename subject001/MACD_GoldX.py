import talib
import numpy as np
import pandas as pd

def macd_goldx(df, atr_mult=3):
    df = df.copy()

    # Calculate MACD and Signal
    macd, macd_signal, _ = talib.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD'] = macd
    df['MACDSignal'] = macd_signal

    # Calculate ATR
    df['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)

    df['Signal'] = np.nan
    position = False
    entry_price = 0

    for i in range(1, len(df)):
        if not position:
            if df.loc[df.index[i - 1], 'MACD'] < df.loc[df.index[i - 1], 'MACDSignal'] and \
               df.loc[df.index[i], 'MACD'] > df.loc[df.index[i], 'MACDSignal']:
                df.loc[df.index[i], 'Signal'] = 1
                position = True
                entry_price = df.loc[df.index[i], 'Close']
        else:
            stop_loss = entry_price - df.loc[df.index[i], 'ATR'] * atr_mult
            if df.loc[df.index[i - 1], 'MACD'] > df.loc[df.index[i - 1], 'MACDSignal'] and \
               df.loc[df.index[i], 'MACD'] < df.loc[df.index[i], 'MACDSignal']:
                df.loc[df.index[i], 'Signal'] = 0
                position = False
            elif df.loc[df.index[i], 'Close'] < stop_loss:
                df.loc[df.index[i], 'Signal'] = 0
                position = False
            else:
                df.loc[df.index[i], 'Signal'] = df.loc[df.index[i - 1], 'Signal']

    df['Signal'].fillna(0, inplace=True)
    return df