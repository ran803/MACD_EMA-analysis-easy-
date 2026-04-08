"""Entry point for MACD strategy backtest."""
import datetime
import json
import os
import sys

import backtrader as bt

from strategies.macd_ema import MacdEmaStrategy


if __name__ == '__main__':
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'data', 'hs300etf.csv')

    cerebro = bt.Cerebro()
    cerebro.addstrategy(
        MacdEmaStrategy,
    )

    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2020, 1, 1),
        todate=datetime.datetime(2025, 1, 1),
        dtformat='%Y-%m-%d',
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
        reverse=False,
    )
    cerebro.adddata(data)

    initial_cash = 100000
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    print(f'using data: {datapath}')
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()[0]

    print(f"期末资金: {cerebro.broker.getvalue():.2f}")
    print("Sharpe:", results.analyzers.sharpe.get_analysis())
    print("DrawDown:", results.analyzers.drawdown.get_analysis())
    print("Returns:", results.analyzers.returns.get_analysis())
    print("Trades:",results.analyzers.trades.get_analysis())
    cerebro.plot(style="candlestick")
