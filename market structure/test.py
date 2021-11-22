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
import backtrader.analyzers as btanalyzers
import backtrader.strategies as btstrats
import pprint

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
    data = bt.feeds.PandasData(dataname=yf.download('TSLA', '2018-01-01', '2019-01-01'))
    # dataname=yf.download('TSLA', '2018-01-01', '2019-01-01')
    # dataname.to_csv("feeder.csv")

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)


    # Analyzers
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe', timeframe=bt.TimeFrame.Months, compression=20)
    cerebro.addanalyzer(btanalyzers.TimeReturn, _name='annual', timeframe=bt.TimeFrame.Years )
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    
    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Run over everything
    thestrats = cerebro.run(maxcpus=1)
    thestrat = thestrats[0]

    print('Sharpe Ratio: ', thestrat.analyzers.mysharpe.get_analysis() )
    print('Annual Ratio: ', thestrat.analyzers.annual.get_analysis() )
    print('Drawdown Ratio: ', thestrat.analyzers.drawdown.get_analysis() )
    cerebro.plot()