import alpaca_backtrader_api as alpaca
import backtrader as bt
import pytz
import pandas as pd
from structure import MarketStructure as ts
from rsi_stack import RSIStack

alpaca_paper = {
    'api_key': 'PK336EARRLVLRSJ2BWDJ',
    'api_secret': 'BUjwqSDgF3sXFmBBIskXnAb0ktklU9gqAWssLtto',
}

ALPACA_KEY_ID = alpaca_paper['api_key']
ALPACA_SECRET_KEY = alpaca_paper['api_secret']
ALPACA_PAPER = False
APCA_API_BASE_URL= "https://paper-api.alpaca.markets"

fromdate = pd.Timestamp(2020,12,1)
todate = pd.Timestamp(2021,8,17)
timezone = pytz.timezone('US/Eastern')

tickers = ['SPY']
timeframes = {
    '15Min':15,
    # '30Min':30,
    # '1H':60,
}
lentimeframes = len(timeframes)


cerebro = bt.Cerebro()


store = alpaca.AlpacaStore(
    key_id=ALPACA_KEY_ID,
    secret_key=ALPACA_SECRET_KEY,
    paper=False
)

cerebro.addstrategy(RSIStack)
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.0)

if not ALPACA_PAPER:
    # print(f"LIVE TRADING")
    broker = store.getbroker()
    cerebro.setbroker(broker)

DataFactory = store.getdata

# for ticker in tickers:
#     for timeframe, minutes in timeframes.items():
#         print(f'Adding ticker {ticker} using {timeframe} timeframe at {minutes} minutes.')
#         d = DataFactory(
#             dataname=ticker,
#             timeframe=bt.TimeFrame.Minutes,
#             compression=minutes,
#             fromdate=fromdate,
#             todate=todate,
#             historical=True)
#         cerebro.adddata(d)

d = DataFactory(
    dataname="BTCUSD",
    timeframe=bt.TimeFrame.Minutes,
    # compression=60,
    # fromdate=fromdate,
    # todate=todate,
    # historical=False
    )
cerebro.adddata(d)

cerebro.run()
print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
cerebro.plot(style='candlestick', barup='green', bardown='red')

