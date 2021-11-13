import os
import sys
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import yfinance as yahoo_finance

yahoo_finance.pdr_override()
from mpl_finance import candlestick2_ohlc
from data_prep import *
from candlestick import *
from indicators.rsi import *


def run(symbol, candle_pattern):

    # args and plot
    args = arguement_parser(tickers='SPY500', period='5d', interval='1m',
                            dif='0.05', time='1200', number='3', min='150')

    fig, (ax1, ax_rsi) = plt.subplots(2, constrained_layout=True)

    # file location
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/{}.csv'.format(symbol))
    raw_df = get_quotes_file(datapath)

    # zigzags
    datapath = os.path.join(modpath, '../datas/{}ZigZags.csv'.format(symbol))
    zigzags = createZigZagPoints(ticker=symbol, dfSeries=raw_df['close']).dropna()
    resistanceFinder(symbol, zigzags, args)
    ax1.plot(zigzags['Value'])
    ax1.title.set_text('{} chart'.format(symbol))
    candlestick2_ohlc(ax1, raw_df['open'], raw_df['high'], raw_df['low'],raw_df['close'], width=0.6, colorup='g', colordown='r')

    #  candlesticks
    candle_df = get_candle_sticks(df=raw_df)
    plot_candle_pattern_with_ohlc(ax1, candle_df, candle_pattern)
    datapath = os.path.join(modpath, '../datas/{}CandleSticks.csv'.format(symbol))
    candle_df.to_csv(datapath, sep='\t')

    # rsi
    rsi_data = computeRSI(raw_df['close'], 13)
    ax_rsi.title.set_text('RSI chart')
    ax_rsi.axhline(0, linestyle='--', alpha=0.1)
    ax_rsi.axhline(20, linestyle='--', alpha=0.5)
    ax_rsi.axhline(30, linestyle='--')
    ax_rsi.axhline(70, linestyle='--')
    ax_rsi.axhline(80, linestyle='--', alpha=0.5)
    ax_rsi.axhline(100, linestyle='--', alpha=0.1)
    ax_rsi.plot(raw_df.index[:-1], rsi_data)
    plt.show()

run("DEMO", "CDLLONGLEGGEDDOJI_Bull")