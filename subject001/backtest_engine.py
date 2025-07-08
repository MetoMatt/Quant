import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt


class BacktestEngine:
    def __init__(self, df, strategy_func, initial_cash = 1):
        self.df = df.copy()
        self.strategy_func = strategy_func
        self.initial_cash = initial_cash

    def run(self):
        self.df = self.strategy_func(self.df)
        self.df['Position'] = self.df['Signal'].shift(1).fillna(0)
        self.df['Return'] = self.df['Close'].pct_change()
        self.df['StrategyReturn'] = self.df['Position'] * self.df['Return']
        self.df['CumulativeReturn'] = (1 + self.df['StrategyReturn']).cumprod() * self.initial_cash
        self.df['CumulativeMarket'] = (1 + self.df['Return']).cumprod() * self.initial_cash
        return self.df

    def plot(self):
        self.df[['CumulativeReturn', 'CumulativeMarket']].plot(figsize=(12, 6), title='Strat vs Market')
        plt.grid(True)
        plt.show()

    def evaluate(self):
        from numpy import sqrt

        r = self.df['StrategyReturn'].dropna()
        win_rate = (r > 0).mean()
        annual_return = r.mean() * 252
        sharpe = r.mean() / r.std() * sqrt(252)

        peak = self.df['CumulativeReturn'].cummax()
        drawdown = self.df['CumulativeReturn'] / peak - 1
        max_drawdown = drawdown.min()

        return {
            "Win Rate": round(win_rate, 4),
            "Annual Return": round(annual_return, 4),
            "Sharpe Ratio": round(sharpe, 4),
            "Max Drawdown": round(max_drawdown, 4)
        }





