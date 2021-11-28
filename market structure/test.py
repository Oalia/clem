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
from extensions.utils import print_sqn, print_trade_analysis, send_telegram_message
from extensions.config import BINANCE, ENV, PRODUCTION, COIN_TARGET, COIN_REFER, DEBUG
from ccxtbt import CCXTStore


def main():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    if ENV == PRODUCTION:  # Live trading with Binance
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret"),
            'nonce': lambda: str(int(time.time() * 1000)),
            'enableRateLimit': True,
        }

        store = CCXTStore(exchange='binance', currency=COIN_REFER, config=broker_config, retries=5, debug=DEBUG)

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.Stop: 'stop-loss',
                bt.Order.StopLimit: 'stop limit'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'status',
                    'value': 'canceled'
                }
            }
        }

        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)

        hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=30000)
        data = store.getdata(
            dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
            name='%s%s' % (COIN_TARGET, COIN_REFER),
            timeframe=bt.TimeFrame.Minutes,
            fromdate=hist_start_date,
            compression=30,
            ohlcv_limit=99999
        )

        # Add the feed
        cerebro.adddata(data)

    else:  
        # Datas are in a subfolder of the samples. Need to find where the script is
        # because it could have been called from anywhere
        # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        # datapath = os.path.join(modpath, '../../datas/data_file.csv')

        data = bt.feeds.PandasData(dataname=yf.download('BTC-USD', '2020-12-01', '2021-11-24', interval="1h"))
        # Add the Data Feed to Cerebro
        cerebro.adddata(data)

        cerebro.broker.setcash(500.0)
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


    if DEBUG:
        cerebro.plot()


    # Run over everything
    thestrat = result[0]
    for each in thestrat.analyzers:
        each.print()


    print('Sharpe Ratio: ', thestrat.analyzers.mysharpe.get_analysis() )
    # print('Annual Ratio: ', thestrat.analyzers.annual.get_analysis() )
    # print('Drawdown Ratio: ', thestrat.analyzers.drawdown.get_analysis() )


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
