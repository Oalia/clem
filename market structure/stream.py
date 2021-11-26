from alpaca_trade_api.stream import Stream

async def trade_callback(t):
    print('trade', t)


async def quote_callback(q):
    print('quote', q)


# Initiate Class Instance
stream = Stream("PK336EARRLVLRSJ2BWDJ",
                "BUjwqSDgF3sXFmBBIskXnAb0ktklU9gqAWssLtto",
                base_url=URL('https://paper-api.alpaca.markets'),
                data_feed='iex')  # <- replace to SIP if you have PRO subscription

# subscribing to event
stream.subscribe_trades(trade_callback, 'AAPL')
stream.subscribe_quotes(quote_callback, 'IBM')

stream.run()