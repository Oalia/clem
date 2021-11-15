
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas_datareader.data as web
import yfinance as yf
from strategies import vortex_strategy as ts
import csv


# Import the backtrader platform
import backtrader as bt

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    # strats = cerebro.optstrategy(
    #     ts.TestStrategy,
    #     maperiod=range(10, 31))
    cerebro.addstrategy(ts.TestStrategy)
    
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/data_file.csv')

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=yf.download('GOLD', '2017-01-01', '2020-10-01'))
    # dataname=yf.download('TSLA', '2018-01-01', '2019-01-01')
    # dataname.to_csv("feeder.csv")

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Run over everything
    cerebro.run(maxcpus=1)
    cerebro.plot()