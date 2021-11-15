import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
# import avg_rel_time

# Create a Stratey
class TestStrategy(bt.Strategy):
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
        # 1. Vortex indicator

        self.vortex = Vortex()
        # self.vi_plus = Vortex().lines.vi_plus
        # self.zig = ZigZag(self.data)
        self.vortex_dif = - self.vortex.vi_plus + self.vortex.vi_minus

        # 3 bollinger bands
        self.boll = bt.indicators.BollingerBands(period=self.p.bollperiod, devfactor=self.p.devfactor)


        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)
        
        self.vortex_sma = bt.indicators.SimpleMovingAverage(Vortex().lines.vi_plus, period=self.params.rsperiod)

        # try:
        #     self.vortex_sma = bt.indicators.SimpleMovingAverage(self.vi_plus[0], period=self.params.maperiod)
        # except Exception as e:
        #     print(e)
             
        
        # 2 RSI
        self.rsi = bt.indicators.RSI(
            self.datas[0], period=self.params.rsperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                # stop_loss = order.executed.price*(1.0 - (self.p.stoploss))
                # take_profit = order.executed.price*(1.0 + self.p.profit_mult*(self.p.stoploss))

                # sl_ord = self.sell(exectype=bt.Order.Stop,
                #                     price=stop_loss)
                # sl_ord.addinfo(name="Stop")

                # tkp_ord = self.sell(exectype=bt.Order.Limit,
                #                     price=take_profit)
                # tkp_ord.addinfo(name="Prof")
                # self.order_dict[sl_ord.ref] = tkp_ord
                # self.order_dict[tkp_ord.ref] = sl_ord

                # if self.p.prorder:
                #     print("SignalPrice: %.2f Buy: %.2f, Stop: %.2f, Prof: %.2f"
                #             % (self.last_sig_price,
                #                 order.executed.price,
                #                 stop_loss,
                #                 take_profit))
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

        # Check if we are in the market
        if not self.position:
            # print(self.vi_plus[0])
            # print(self.vortex_dif[0])
            # if round(self.rsi[0]) == 27 and self.vortex.vi_minus[0]:
            if round(self.vortex.vi_minus[0], 1) < 0.48:
            # if round(self.vortex_dif[0], 3) < 0.001 : 
                # if self.data.close < self.boll.lines.bot:

                # if round(self.vortex_dif[4], 2) > 0.1 :
                #if self.vortex.vi_minus[0] - self.vortex.vi_plus[0] < 0.009 : # and self.vortex.l.vi_minus[10] > 1:
                # print(self.vortex.vi_minus[0], self.vortex.vi_plus[0])
                #if self.vortex_sma[0] < self.vortex.l.vi_minus[0]: #self.vortex.vi_plus[0] or self.vortex_sma[3] < self.vortex.vi_plus[0]:
                    # if self.dataclose[0] < self.sma[0]:
                        # if self.vortex.vi_plus[0] <= 0.75: # or self.vortex.vi_minus[0] > 1.09:
                        # Not yet ... we MIGHT BUY if ...
                        #if self.dataclose[0] < self.sma[0] and self.dataclose[0] < self.zig.last_high[0]:
                            #if self.rsi[0] < 30:
                                # BUY, BUY, BUY!!! (with all possible default parameters)
                                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                                # Keep track of the created order to avoid a 2nd order
                                self.order = self.buy()

        else:
            # if round(self.rsi[0]) == 60:
            if self.data.close >= self.boll.lines.top:
                # if round(self.rsi[0]) >= 70:
                # if round(self.vortex_dif[0], 2) < -0.31:

            # if self.vortex_dif[0] < - 0.7 and self.rsi[0] > 60:
            # if self.dataclose[0] > self.sma[0]:
                # if self.vortex.vi_plus[0] >= 1.12: # or self.vortex.vi_minus[0] < .55:
                #if self.dataclose[0] > self.sma[0]:
                    #if self.rsi[0] > 76:
                        # SELL, SELL, SELL!!! (with all possible default parameters)
                        
                        self.log('SELL CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.sell()


    def stop(self):
        self.log('(MA Period %2d) Ending Value %.2f' %
                 (self.params.maperiod, self.broker.getvalue()), doprint=True)

class Vortex(bt.Indicator):
    '''
    See:
      - http://www.vortexindicator.com/VFX_VORTEX.PDF
    '''
    lines = ('vi_plus', 'vi_minus',)
    params = (('period', 14),)

    plotlines = dict(vi_plus=dict(_name='+VI', ls='--'), vi_minus=dict(_name='-VI'))

    def __init__(self):
        h0l1 = abs(self.data.high(0) - self.data.low(-1))
        vm_plus = bt.ind.SumN(h0l1, period=self.p.period)

        l0h1 = abs(self.data.low(0) - self.data.high(-1))
        vm_minus = bt.ind.SumN(l0h1, period=self.p.period)

        h0c1 = abs(self.data.high(0) - self.data.close(-1))
        l0c1 = abs(self.data.low(0) - self.data.close(-1))
        h0l0 = abs(self.data.high(0) - self.data.low(0))

        tr = bt.ind.SumN(bt.Max(h0l0, h0c1, l0c1), period=self.p.period)

        self.l.vi_plus = vm_plus / tr
        self.l.vi_minus = vm_minus / tr


class ZigZag(bt.ind.PeriodN):
    '''
      ZigZag indicator.
    '''
    lines = (
        'trend',
        'last_high',
        'last_low',
        'zigzag',
    )

    plotinfo = dict(
        subplot=False,
        plotlinelabels=True, plotlinevalues=True, plotvaluetags=True,
    )

    plotlines = dict(
        trend=dict(_plotskip=True),
        last_high=dict(color='green', ls='-', _plotskip=True),
        last_low=dict(color='black', ls='-', _plotskip=True),
        zigzag=dict(_name='zigzag', color='blue', ls='-', _skipnan=True),
    )

    params = (
        ('period', 2),
        ('retrace', 0.05), # in percent
        ('minbars', 2), # number of bars to skip after the trend change
    )

    def __init__(self):
        super(ZigZag, self).__init__()

        assert self.p.retrace > 0, 'Retracement should be above zero.'
        assert self.p.minbars >= 0, 'Minimal bars should be >= zero.'

        self.ret = self.data.close * self.p.retrace / 100
        self.minbars = self.p.minbars
        self.count_bars = 0
        self.last_pivot_t = 0
        self.last_pivot_ago = 0

    def prenext(self):
        self.l.trend[0] = 0
        self.l.last_high[0] = self.data.high[0]
        self.l.last_low[0] = self.data.low[0]
        self.l.zigzag[0] = (self.data.high[0] + self.data.low[0]) / 2

    def next(self):
        curr_idx = len(self.data)
        self.ret = self.data.close[0] * self.p.retrace / 100
        self.last_pivot_ago = curr_idx - self.last_pivot_t
        self.l.trend[0] = self.l.trend[-1]
        self.l.last_high[0] = self.l.last_high[-1]
        self.l.last_low[0] = self.l.last_low[-1]
        self.l.zigzag[0] = float('nan')

        # Search for trend
        if self.l.trend[-1] == 0:
            if self.l.last_low[0] < self.data.low[0] and self.l.last_high[0] < self.data.high[0]:
                self.l.trend[0] = 1
                self.l.last_high[0] = self.data.high[0]
                self.last_pivot_t = curr_idx

            elif self.l.last_low[0] > self.data.low[0] and self.l.last_high[0] > self.data.high[0]:
                self.l.trend[0] = -1
                self.l.last_low[0] = self.data.low[0]
                self.last_pivot_t = curr_idx

        # Up trend
        elif self.l.trend[-1] == 1:
            if self.data.high[0] > self.l.last_high[-1]:
                self.l.last_high[0] = self.data.high[0]
                self.count_bars = self.minbars
                self.last_pivot_t = curr_idx

            elif self.count_bars <= 0 and self.l.last_high[0] - self.data.low[0] > self.ret and self.data.high[0] < self.l.last_high[0]:
                self.l.trend[0] = -1
                self.count_bars = self.minbars
                self.l.last_low[0] = self.data.low[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_high[0]
                self.last_pivot_t = curr_idx

            elif self.count_bars < self.minbars and self.data.close[0] < self.l.last_low[0]:
                self.l.trend[0] = -1
                self.count_bars = self.minbars
                self.l.last_low[0] = self.data.low[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_high[0]
                self.last_pivot_t = curr_idx

        # Down trend
        elif self.l.trend[-1] == -1:
            if self.data.low[0] < self.l.last_low[-1]:
                self.l.last_low[0] = self.data.low[0]
                self.count_bars = self.minbars
                self.last_pivot_t = curr_idx

            elif self.count_bars <= 0 and self.data.high[0] - self.l.last_low[0] > self.ret and self.data.low[0] > self.l.last_low[0]:
                self.l.trend[0] = 1
                self.count_bars = self.minbars
                self.l.last_high[0] = self.data.high[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_low[0]
                self.last_pivot_t = curr_idx

            elif self.count_bars < self.minbars and self.data.close[0] > self.l.last_high[-1]:
                self.l.trend[0] = 1
                self.count_bars = self.minbars
                self.l.last_high[0] = self.data.high[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_low[0]
                self.last_pivot_t = curr_idx

        # Decrease minbars counter
        self.count_bars -= 1