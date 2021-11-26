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
        ('stop_loss', 0.34),
        ('profit_mult', 0.2),
        ('trail', False),
        
    )

    # keeps track of buy order for stop loss
    buy_order = None
    sell_order = None

    def logdata(self):
        txt = []
        txt.append('{}'.format(len(self)))
           
        txt.append('{}'.format(
            self.data.datetime.datetime(0).isoformat())
        )
        txt.append('{:.2f}'.format(self.data.open[0]))
        txt.append('{:.2f}'.format(self.data.high[0]))
        txt.append('{:.2f}'.format(self.data.low[0]))
        txt.append('{:.2f}'.format(self.data.close[0]))
        txt.append('{:.2f}'.format(self.data.volume[0]))
        print(','.join(txt))

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
        self.nullzig = ZigZag(self.data)
        # support and resistance
        self.supres = SupportResistance(self.nullzig)

        # 3 bollinger bands
        self.boll = bt.indicators.BollingerBands(period=self.p.bollperiod, devfactor=self.p.devfactor)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            print("order submitted / Accepted")
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
                print(self.buyprice, "buy order complete")

            elif order.issell():  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)
            print(order.executed.price, "sell order complete")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # write down: no pending order
        if order.status in [order.Completed, order.Cancelled, order.Rejected]:
            self.order = None


    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        self.logdata()
        
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            print("order pending")
            return            

        # Check if we are in the market
        if not self.position:
            if self.buy_order: # some order was pending
                self.cancel(self.buy_order)
            
            # do nothing if the trend is already in motion
            if not (self.nullzig.l.zigzag[0] >= 0) :
                ""
            else:
                # if self.dataclose[0] < self.boll.bot[0]:
                    # else when we note a change in trend, then work
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    # keep track of the created order to avoid a 2nd order
                    # transmit = False, means the order will be transmitted from a child order
                    self.order = self.sell()

                    # self.buy_order = self.buy(transmit=False)

                    # #Setting parent=buy_order ... sends both together
                    # if not self.p.trail:
                    #     stop_price = self.data.close[0] * (1.0 - self.p.stop_loss)
                    #     self.sell(exectype=bt.Order.Stop, price=stop_price,
                    #             parent=self.buy_order)
                    # else:
                    #     self.sell(exectype=bt.Order.StopTrail,
                    #           trailamount=self.p.trail,
                    #           parent=self.buy_order)

        else:

            # do nothing if the trend is already in motion
            if not (self.nullzig.l.zigzag[0] >= 0) :
                ""
            else:
                # if self.nullzig.l.zigzag[0] == 1:
                    # else when we note a change in trend, then work
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    # keep track of the created order to avoid a 2nd order
                    self.sell_order = self.buy()

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
    
    