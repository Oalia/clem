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


ALPACA_API_KEY = "PK336EARRLVLRSJ2BWDJ"
ALPACA_SECRET_KEY = "BUjwqSDgF3sXFmBBIskXnAb0ktklU9gqAWssLtto"
ALPACA_PAPER = True


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ts)


    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=ALPACA_PAPER
    )

    if not ALPACA_PAPER:
        broker = store.getbroker()  # or just alpaca_backtrader_api.AlpacaBroker()
        cerebro.setbroker(broker)

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    data0 = DataFactory(dataname='AAPL', historical=True, fromdate=datetime(
        2020, 1, 1), timeframe=bt.TimeFrame.Days)
    print(data0)

    cerebro.adddata(data0)

    # Analyzers
    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(btanalyzers.TimeReturn, _name='annual', timeframe=bt.TimeFrame.Years )
    cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
    
    # Set our desired cash start
    cerebro.broker.setcash(50000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 80)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    thestrats = cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())    
    thestrat = thestrats[0]

    print('Sharpe Ratio: ', thestrat.analyzers.mysharpe.get_analysis() )
    print('Annual Ratio: ', thestrat.analyzers.annual.get_analysis() )
    print('Drawdown Ratio: ', thestrat.analyzers.drawdown.get_analysis() )
    cerebro.plot()