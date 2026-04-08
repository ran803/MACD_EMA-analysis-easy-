"""MACD + EMA strategy placeholder."""
import backtrader as bt

class MacdEmaStrategy(bt.Strategy):
    params = dict(
        ema_fast=12,
        ema_slow=26,
        signal_period=9, # 信号线（DEA）的周期，即对DIF取EMA的周期
        trend_ema=60,
        printlog=True,
    )

    def log(self, txt,dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s,%s" %(dt.isoformat(),txt))

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.trend_ema = bt.indicators.ExponentialMovingAverage(
            self.dataclose,period=self.params.trend_ema
        )
        self.macd = bt.indicators.MACD(
            self.dataclose,
            period_me1=self.params.ema_fast,
            period_me2=self.params.ema_slow,
            period_signal=self.params.signal_period
        )
        # CrossOver 会逐根K线比较 fast_ma 和 slow_ma 的数值。
        # CrossOver 返回一个信号序列.1:快线上穿慢线（金叉）；0:没有交叉；-1：快线下穿慢线（死叉）
        # self.macd.macd：MACD的快线（DIF = EMA12 - EMA26）。
        # self.macd.signal：MACD的慢线（DEA = DIF的9日EMA）。
        self.crossover = bt.indicators.CrossOver(self.macd.macd,self.macd.signal)
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("买入价格：%.2f,数量为：%d" % (order.executed.price,order.executed.size))
            elif order.issell():
                self.log("卖出价格：%.2f,数量为：%d" % (order.executed.price,order.executed.size))
        elif order.status in [order.Rejected]:
            self.log("订单被取消 / 保证金不足 / 拒绝")

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed: # pnl: Profit and Loss
            self.log("本次交易毛利润：%.2f,净利润：%.2f" % (trade.pnl, trade.pnlcomm))

    def next(self):
        if self.order:
            return

        price_above_trend = self.datas[0].close[0] > self.trend_ema[0]
        if not self.position:
            if price_above_trend and self.crossover > 0:
                self.log(f"MACD 金叉买入, Close={self.datas[0].close[0]:.2f}")
                self.order = self.buy(size=100)
        else:
            if self.crossover < 0 or self.datas[0].close[0] < self.trend_ema[0]:
                self.log(f"MACD 死叉/跌破趋势均线卖出, Close={self.datas[0].close[0]:.2f}")
                self.order = self.sell(size=100)


