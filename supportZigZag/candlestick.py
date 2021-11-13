from candle_rankings import candle_rankings
import talib
from itertools import compress
import numpy as np
import yfinance as yahoo_finance
yahoo_finance.pdr_override()


def get_candle_sticks(df):
    """Adds candlestick to the rows of our data using the TAlib library

    Parameters
    ----------
    df : pandas df of ohlc
        The data we want to assign candlesticks to it's rows

    Returns
    -------
    df: pandas df 
        It returns a dataframe with candlestick patterns assigned to the last row
    """

    op = df['open']
    hi = df['high']
    lo = df['low']
    cl = df['close']

    candle_names = talib.get_function_groups()['Pattern Recognition']
    # patterns not found in the patternsite.com
    exclude_items = ('CDLCOUNTERATTACK',
                     'CDLLONGLINE',
                     'CDLSHORTLINE',
                     'CDLSTALLEDPATTERN',
                     'CDLKICKINGBYLENGTH')
    candle_names = [candle for candle in candle_names if candle not in exclude_items]

    # create columns for each pattern and set values to each row using getattr 
    for candle in candle_names:
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)

    # will be used to set candle pattern value of a row 
    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan

    for index, row in df.iterrows():
        # no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index, 'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                else:
                    container.append(pattern + '_Bear')
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    cols_to_drop = candle_names
    df.drop(cols_to_drop, axis=1, inplace=True)
    return df


def plot_candle_pattern_with_ohlc(plt, candles_df, pattern):
    xs = candles_df.index
    ys = candles_df['close']

    for x,y in zip(xs,ys):
        if x >= 0 and x < len(xs):
            candle = candles_df['candlestick_pattern'].values[x]
            if pattern == candle:
                label = "{}".format(candle)

                plt.annotate(label, 
                            (x,y),
                            textcoords="offset points",
                            rotation=90,
                            size = 5,
                            va='center',
                            xytext=(10,0),
                )