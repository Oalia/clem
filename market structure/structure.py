import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
from zigzag import *
from supres import SupportResistance
import requests
import datetime as dt


TELEGRAM = {
  "channel": "-1001683168351", 
  "bot": "2124069658:AAG9Q_NXP3PajsxDD58yn4tnRrK3rFWs8-U"
}
# TELEGRAM = {
#   "channel": "-1759912824", 
#   "bot": "5034003189:AAEVr7ycuuWhGj69B8lMZJ_uRJMWtWYUFXw"
# }


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

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # print("order submitted / Accepted")
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.send_telegram_message("BUY EXECUTED, Price: {}, Cost: {}, Comm {}".format(order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                # print(self.buyprice, "buy order complete")

            elif order.issell():  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.send_telegram_message("SELL EXECUTED, Price: {}, Cost: {}, Comm {}".format(order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            self.bar_executed = len(self)
            # print(order.executed.price, "sell order complete")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            self.send_telegram_message("Order Canceled/Margin/Rejected")

        # write down: no pending order
        if order.status in [order.Completed, order.Cancelled, order.Rejected]:
            self.order = None
            ""


    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
        self.send_telegram_message("OPERATION PROFIT, GROSS {}, NET {}".format(trade.pnl, trade.pnlcomm))
        # print('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
        #          (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # self.logdata()
        
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
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                    # keep track of the created order to avoid a 2nd order
                    # transmit = False, means the order will be transmitted from a child order
                self.order = self.buy()
                self.send_telegram_message("BUY CREATE {} {}".format(self.data.datetime.datetime(0).isoformat(), self.dataclose[0]))
        else:

            # do nothing if the trend is already in motion
            if not (self.nullzig.l.zigzag[0] >= 0) :
                ""
            else:
                # if self.nullzig.l.zigzag[0] == -1:
                    # print(self.nullzig.l.zigzag[0], " SELL")
                    # else when we note a change in trend, then work
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])

                    # keep track of the created order to avoid a 2nd order
                    self.sell_order = self.sell()
                    self.send_telegram_message("SELL CREATE {} {}".format(self.data.datetime.datetime(0).isoformat(), self.dataclose[0]))

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

    def send_telegram_message(self, message):
        # if ENV != "production":
        #     return

        base_url = "https://api.telegram.org/bot%s" % TELEGRAM.get("bot")
        requests.get("%s/sendMessage" % base_url, params={
            'chat_id': TELEGRAM.get("channel"),
            'text': message
        })
    
    """
     API Key: h51BzWIJPFEWsiwrtSEZrPbd9hg1RBLYA4Obt4648xvk6Ui9L13S75e8oPExxKcX

Secret Key: 28612dc1YDdd4kDWljRSRZh3Zg63nI4AvfoViW2Xrdn5u777jKefzKBNSykZS8ce
    ""
    """
   