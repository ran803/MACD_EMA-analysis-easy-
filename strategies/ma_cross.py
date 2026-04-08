import backtrader as bt
from datetime import datetime

class MovingAverageCrossStrategy(bt.Strategy):
    params = dict(
        fast_period=10,
        slow_period=20,
        printlog=True,
    )

    def log(self, txt,dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s,%s" %(dt.isoformat(),txt))

    def __init__(self):
        self.dataclose = self.datas[0].close

        self.fast_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.p.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.p.slow_period)

        # CrossOver 会逐根K线比较 fast_ma 和 slow_ma 的数值。
        # CrossOver 返回一个信号序列.1:快线上穿慢线（金叉）；0:没有交叉；-1：快线下穿慢线（死叉）
        self.crossover = bt.indicators.CrossOver(self.fast_ma,self.slow_ma)
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
        if not self.position:
            if self.crossover>0:
                self.log("买入信号，close=%.2f" % self.dataclose[0])
                self.order = self.buy(size=100)
        else:
            if self.crossover<0:
                self.log("卖出信号，close=%.2f" % self.dataclose[0])
                self.order = self.sell(size=100)


