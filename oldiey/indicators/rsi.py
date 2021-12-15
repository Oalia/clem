import numpy as np
def computeRSI (data, time_window):
    diff = data.diff(1).dropna()        # diff in one field(one day)
    #this preservers dimensions off diff values
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]
    
    # check pandas documentation for ewm
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    # values are related to exponential decay
    # we set com=time_window-1 so we get decay alpha=1/time_window
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    return rsi

def rsi(df, n=13):
    close_df = df['close']
    deltas = np.diff(close_df)
    seed = deltas[:n+1]

    up = seed[seed>= 0].sum()/n
    down = seed[seed< 0].sum()/n
    rs = up/down

    rsi = np.zeros_like(close_df)
    rsi[:n] = 100. -100/(1. +rs)
    for i in range(n, len(close_df)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n-1)+downval)/n
        down = (down*(n-1)+downval)/n
        rs = up/down
        rsi[i] = 100. -100./(1.+rs)
    return rsi

# def rsi(df):
#     close_df = df['close']
#     delta = close_df.diff()
#     up =  delta.clip(lower=0)
#     down = -1*delta.clip(upper=0)
#     ema_up = up.ewm(com=13, adjust=False).mean()
#     ema_down = down.ewm(com=13, adjust=False).mean()
#     rs = ema_up/ema_down

#     df['rsi'] = 100 - (100/1+rs)
#     df = df.iloc[14:]

#     return df
