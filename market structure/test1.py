from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects 
import os.path  # To manage paths
import datetime as dt
from backtrader.dataseries import TimeFrame  # To find out the script name (in argv[0])
import pandas_datareader.data as web
import yfinance as yf
from structure import MarketStructure as ts
import backtrader as bt
import backtrader.analyzers as btan
import backtrader.strategies as btstrats
import pprint
from extensions.analyzers import BasicTradeStats


def main():
    # Create a cerebro entity
    cerebro = bt.Cerebro()


        # Datas are in a subfolder of the samples. Need to find where the script is
        # because it could have been called from anywhere
        # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        # datapath = os.path.join(modpath, '../../datas/data_file.csv')

    data = bt.feeds.PandasData(dataname=yf.download('BNB-USD', '2020-12-11', dt.datetime.utcnow(), interval="1h"))
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.broker.setcash(10.0)
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 90)
    cerebro.broker.setcommission(commission=0.002)
    

     # Analyzers
    cerebro.addanalyzer(btan.SharpeRatio, _name='mysharpe')
    # cerebro.addanalyzer(btan.TimeReturn, _name='annual', timeframe=bt.TimeFrame.Years )
    cerebro.addanalyzer(btan.DrawDown, _name='drawdown')

    cerebro.addanalyzer(BasicTradeStats, _name="BasicTradeStats", )
    # cerebro.addanalyzer(BasicTradeStats, _name="BasicTradeStats", )
    cerebro.addanalyzer(btan.SQN)


    # Add a strategy
    # strats = cerebro.optstrategy(
    #     ts.TestStrategy,
    #     maperiod=range(10, 31))
    cerebro.addstrategy(ts)


    # Starting backtrader bot
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()



    # Run over everything
    thestrat = result[0]
    for each in thestrat.analyzers:
        each.print()


    print('Sharpe Ratio: ', thestrat.analyzers.mysharpe.get_analysis() )
    # print('Annual Ratio: ', thestrat.analyzers.annual.get_analysis() )
    # print('Drawdown Ratio: ', thestrat.analyzers.drawdown.get_analysis() )
    cerebro.plot()


if __name__== "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("finished.")
        # time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        # send_telegram_message("Bot finished by user at %s" % time)
    except Exception as err:
        # send_telegram_message("Bot finished with error: %s" % err)
        print("Finished with error: ", err)
        raise
