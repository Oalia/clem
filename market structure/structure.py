import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
from zigzag import *
from supres import SupportResistance



# Create a Stratey
class MarketStructure(bt.Strategy):
    """
    market trend: bullish
    not suitable to a downward trending market
    """
    params = (

        ('maperiod', 15),
        ('devfactor', 1.6),
        ('bollperiod', 9),
        ('rsperiod', 9),
        ('printlog', False),
        ('stoploss', 0.01),
        ('profit_mult', 0.2),
        ('trail', False),
        
    )

    # keeps track of buy order for stop loss
    buy_order = None

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
  
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # zigzags
        self.nullzig = ZigZag(self.data)\
        # support and resistance
        self.supres = SupportResistance(self.nullzig)

        # 3 bollinger bands
        # self.boll = bt.indicators.BollingerBands(period=self.p.bollperiod, devfactor=self.p.devfactor)

        # Add a MovingAverageSimple indicator
        # self.sma = bt.indicators.SimpleMovingAverage(
        #     self.datas[0], period=self.params.maperiod)
        
        # 2 RSI
        # self.rsi = bt.indicators.RSI(
        #     self.datas[0], period=self.params.rsperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')


    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        # if self.order:
        #     return

        # zigzags
        # if self.nan_zig.zigzag[0] > 0:
            # """ """
        # print(len(self.nullzig))
        # try: 
        #     # print(len(self.zigs))
        # except:
        #     """"""


        # print(self .nan_zig.zigzag[0] , self.nan_zig.value[0])
            

        # Check if we are in the market
        # if not self.position:
            # self.order = self.buy()

        # else:
         
        # self.order = self.sell()

    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)
        support = self.supres.l.support.get(size = len(self.supres))
        df = pd.DataFrame(support)
        df = df.dropna()
        df.to_csv("supports.csv")

        resistance = self.supres.l.support.get(size = len(self.supres))
        df = pd.DataFrame(resistance)
        df = df.dropna()
        df.to_csv("resistances.csv")
        