from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects 
import os.path  # To manage paths
import sys
from backtrader.dataseries import TimeFrame  # To find out the script name (in argv[0])
import pandas_datareader.data as web
import yfinance as yf
from structure import MarketStructure as ts
import backtrader as bt
import backtrader.analyzers as btan
import backtrader.strategies as btstrats
import pprint
from extensions.analyzers import BasicTradeStats

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
        # strats = cerebro.optstrategy(
        #     ts.TestStrategy,
        #     maperiod=range(10, 31))
    cerebro.addstrategy(ts)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/data_file.csv')

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=yf.download('ETH-USD', '2020-12-01', '2021-11-24', interval="1h"))
    # dataname=yf.download('TSLA', '2018-01-01', '2019-01-01')
    # dataname.to_csv("feeder.csv")

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)


    # Analyzers
    cerebro.addanalyzer(btan.SharpeRatio, _name='mysharpe')
    # cerebro.addanalyzer(btan.TimeReturn, _name='annual', timeframe=bt.TimeFrame.Years )
    cerebro.addanalyzer(btan.DrawDown, _name='drawdown')

    cerebro.addanalyzer(BasicTradeStats, _name="BasicTradeStats", )
    # cerebro.addanalyzer(BasicTradeStats, _name="BasicTradeStats", )
    cerebro.addanalyzer(btan.SQN)
    
    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 50)

    # Set the commission
    cerebro.broker.setcommission(commission=0.002)

    # Run over everything
    thestrats = cerebro.run(maxcpus=1)
    thestrat = thestrats[0]

    for each in thestrat.analyzers:
        each.print()


    print('Sharpe Ratio: ', thestrat.analyzers.mysharpe.get_analysis() )
    # print('Annual Ratio: ', thestrat.analyzers.annual.get_analysis() )
    # print('Drawdown Ratio: ', thestrat.analyzers.drawdown.get_analysis() )
    cerebro.plot()