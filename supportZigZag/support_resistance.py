import os
import sys
import pandas as pd
import csv
import yfinance as yahoo_finance
yahoo_finance.pdr_override()
import numpy as np



def createZigZagPoints(ticker, dfSeries, minSegSize=0.1):
    """Finds and returns Zigzag points in ticker's dataseries 

    Parameters
    ----------
    ticker: str
            Ticker name. Used for appending zigzag datapoints to CSV
    dfSeries: pd.Series
            The series data that their zigzag points are being searched for
    minSegSize: float
            Used to show the minimum retracement that potentially triggers a
            new zigzag

    Returns
    -------
    pd.Series
            a data series of retracement points that form zigzag lines
            TODO: the data series returned has some indexed empty values 
    
    Algorithm:
    For each index representing a data point, it looks for changes in next value that are trending
    If the next value is trending, that value becomes the index
    If not, we check the retracement from the trend. If the retracement is more than some minRetrace,
    we add our old index's values to our zigzag dataframe. The datapoint with the given retracement becomes the new
    index.
    """

    minRetrace = minSegSize
    curVal = dfSeries[0]
    curPos = dfSeries.index[0]
    curDir = 1
    dfZigZag = pd.DataFrame(index=dfSeries.index, columns=["Dir", "Value"])
    for ln in dfSeries.index:
        if((dfSeries[ln] - curVal)*curDir >= 0):
            curVal = dfSeries[ln]
            curPos = ln
        else:
            retracePrc = abs((dfSeries[ln]-curVal)/curVal*100)
            if(retracePrc >= minRetrace):
                dfZigZag.loc[curPos, 'Value'] = curVal
                dfZigZag.loc[curPos, 'Dir'] = curDir
                appendToCSV('{}ZigZag.csv'.format(ticker), [curVal, curDir])
                curVal = dfSeries[ln]
                curPos = ln
                curDir = -1*curDir
    return dfZigZag


def resistanceFinder(ticker, dfRes, args, plt):
    """Gets Support and Resistance points that last forever

    Parameters
    ----------
    ticker : str
            Ticker name. Used for appending support/resistance datapoints to CSV
    dfRes : pd.Series
            Zigzag datapoints that are worked on

    Returns
    -------
    endx. It helps maintain temporal continuity between this method and drawTicker

    Algorithm
    ---------
    Using input dataframe of zigzag points, we iterate the dataframe, marking each index for removal
    in the future by addig them to a removed_index list. Then for that index, we run an inner for 
    loop across the remaining datapoints. If the datapoints have a difference that is within a small range,
    then they are support/resistance.
    """

    try:
        x_max = 0
        removed_indexes = []
        for index, row in dfRes.iterrows():
            if (not(index in removed_indexes)):
                dropindexes = []
                dropindexes.append(index)
                counter = 0
                values = []
                values.append(row.Value)
                startx = index
                endx = index
                dir = row.Dir
                for index2, row2 in dfRes.iterrows():
                    if (not(index2 in removed_indexes)):
                        if (index != index2 and abs(index2-index) < args.time and row2.Dir == dir):
                            if (abs((row.Value/row2.Value)-1) < (args.dif/100)):
                                dropindexes.append(index2)
                                values.append(row2.Value)
                                if (index2 < startx):
                                    startx = index2
                                elif (index2 > endx):
                                    endx = index2
                                counter = counter+1

                if (counter > args.number):
                    sum = 0
                    print("Support at ", end='')
                    for i in range(len(values)-1):
                        print("{:0.2f} and ".format(values[i]), end='')
                    print("{:0.2f} \n".format(values[len(values)-1]), end='')
                    removed_indexes.extend(dropindexes)
                    for value in values:
                        sum = sum + value
                    if (endx > x_max):
                        x_max = endx
                    plt.hlines(y=sum/len(values), xmin=startx,
                               xmax=endx, linewidth=1, color='r')
                    # for real time/ historical purpose
                    appendToCSV("{}SupportResistance.csv".format(ticker), [sum/len(values), dir])
                    ret = endx
        # return ret
    except Exception as e:
        print(e)


def appendToCSV(filename, data_point):
    """Appends datapoint or dataframe to given csv

    Parameters
    ----------
    filename : str
            Name of file that we are to append data to
    data_point : list or dataframe
            The data we are appending to csv

    Returns
    -------
    -
    """

    if isinstance(data_point, pd.DataFrame):
        data_point.to_csv(filename, mode='a')
    
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/{}'.format(filename))

    file = open(datapath, 'a')
    writer = csv.writer(file)
    writer.writerow(data_point)
    file.close
