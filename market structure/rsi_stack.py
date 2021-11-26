from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import alpaca_backtrader_api
import datetime  # For datetime objects 
import os.path  # To manage paths
import sys
from backtrader.dataseries import TimeFrame  # To find out the script name (in argv[0])
import pandas_datareader.data as web
import yfinance as yf
from structure import MarketStructure as ts
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.strategies as btstrats
from datetime import datetime


class RSIStack(bt.Strategy):
    params = dict(
        rsi_overbought=70,
        rsi_oversold=30,
        rrr=2
    )

    def __init__(self):
        self.orefs = None
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]['rsi'] = bt.ind.RSI(d)
            self.inds[d]['rsiob'] = self.inds[d]['rsi'] >= self.p.rsi_overbought
            self.inds[d]['rsios'] = self.inds[d]['rsi'] <= self.p.rsi_oversold
        for i in range(len(timeframes)-1, len(self.datas), len(timeframes)):
            self.inds[self.datas[i]]['atr'] = bt.ind.ATR(self.datas[i])

    def start(self):
        # Timeframes must be entered from highest to lowest frequency.
        # Getting the length of the lowest frequency timeframe will
        # show us how many periods have passed
        self.lenlowtframe = len(self.datas[-1])
        self.stacks = {}


    def next(self):
        # Reset all of the stacks if a bar has passed on our
        # lowest frequency timeframe
        if not self.lenlowtframe == len(self.datas[-1]):
            self.lenlowtframe += 1
            self.stacks = {}
        for i, d in enumerate(self.datas):
            # Create a dictionary for each new symbol.
            ticker = d.p.dataname
            if i % len(timeframes) == 0:
                self.stacks[ticker] = {}
                self.stacks[ticker]['rsiob'] = 0
                self.stacks[ticker]['rsios'] = 0
            if i % len(timeframes) == len(timeframes) -1:
                self.stacks[ticker]['data'] = d
            self.stacks[ticker]['rsiob'] += self.inds[d]['rsiob'][0]
            self.stacks[ticker]['rsios'] += self.inds[d]['rsios'][0]

        for k,v in list(self.stacks.items()):
            if v['rsiob'] < len(timeframes) and v['rsios'] < len(timeframes):
                del self.stacks[k]

        # Check if there are any stacks from the previous period
        # And buy/sell stocks if there are no existing positions or open orders
        positions = [d for d, pos in self.getpositions().items() if pos]
        if self.stacks and not positions and not self.orefs:
                for k,v in self.stacks.items():
                    d = v['data']
                    size = self.broker.get_cash() // d
                    if v['rsiob'] == len(timeframes) and \
                                     d.close[0] < d.close[-1]:
                        print(f"{d.p.dataname} overbought")
                        risk = d + self.inds[d]['atr'][0]
                        reward = d - self.inds[d]['atr'][0] * self.p.rrr
                        os = self.sell_bracket(data=d,
                                               price=d.close[0],
                                               size=size,
                                               stopprice=risk,
                                               limitprice=reward)
                        self.orefs = [o.ref for o in os]
                    elif v['rsios'] == len(timeframes) and d.close[0] > d.close[-1]:
                        print(f"{d.p.dataname} oversold")
                        risk = d - self.inds[d]['atr'][0]
                        reward = d + self.inds[d]['atr'][0] * self.p.rrr
                        os = self.buy_bracket(data=d,
                                              price=d.close[0],
                                              size=size,
                                              stopprice=risk,
                                              limitprice=reward)
                        self.orefs = [o.ref for o in os]


    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print(f'{dt.isoformat()}: {txt}')

    def notify_trade(self, trade):
        if not trade.size:
            print(f'Trade PNL: ${trade.pnlcomm:.2f}')

    def notify_order(self, order):
        self.log(f'Order - {order.getordername()} {order.ordtypename()} {order.getstatusname()} for {order.size} shares @ ${order.price:.2f}')

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)

