import backtrader as bt
import backtrader.indicators as btind
import backtrader.feeds as btfeeds
from csv import writer

class SupportResistance(bt.ind.PeriodN):
    """
    Returns two datafeeds that hold nan when no support or resistance value is seen
    
    Support Resistance takes in zig zag feed. Returns support and resistance line feeds
    for each entry in the feed, it should return nan for entry if 
        no support resistance is found.
    Else it should return sup_res, and direction for that time feed.

    """
    lines = (
        'support', # contains 'nan' values for data points that are not pivots
        'resistance', # contains 'nan' values for data points that are not pivots
        
        # to be checked when we get new values
        'last_sup'
        'last_res'
    )

    plotinfo = dict(
        subplot=False,
        plotlinelabels=True, plotlinevalues=True, plotvaluetags=True,
        # plotyhlines = [dict(_name ='support'), dict(_name="resistance")]
    )

    plotlines = dict(
        support=dict(_name='Suppport', color='red', ls='-', _skipnan=True),
        resistance=dict(_name='Resistance', color='green', ls='-', _skipnan=True),
    )

    params = (
        ('sup_counter', 4),
        ('res_counter', 4),
        ('difference', 150)
    )

    def __init__(self):        
        self.last_sup = []
        self.last_res = []
    
        self.res_count = 0
        self.sup_count = 0

    def next(self):
        if self.data.l.zigzag[0] >= 0:
            if self.data.l.value[0] == 1:
                self.last_res.append(self.data.l.zigzag[0])
                self.res_count += 1
                if self.res_count == self.p.res_counter:
                    self.res_count = 0
                    sum = 0
                    count = 0
                    for res in reversed (self.last_res):
                        if count >= 2: # 2 is an arbitrary number.
                            break
                        if (abs((self.data.l.zigzag[0]/res)-1) < (self.params.difference/100)):
                            sum += res
                            count += 1
                    if count >= 2: # 2 is an arbitrary number.
                        self.l.resistance[0] = sum/count
                        count = 0
                    else:
                        self.l.resistance[0] = float('NaN')
                        count = 0

            elif self.data.l.value[0] == -1:
                self.last_sup.append(self.data.l.zigzag[0])
                self.sup_count += 1
                if self.sup_count == self.p.sup_counter:
                    self.sup_count = 0
                    sum = 0
                    count = 0
                    for res in reversed (self.last_sup):
                        if count >= 2: # 2 is an arbitrary number.
                            break
                        elif (abs((self.data.l.zigzag[0]/res)-1) < (self.params.difference/100)):
                            sum += res
                            count += 1
                    if count >= 2: # 2 is an arbitrary number.
                        self.l.support[0] = sum/count
                        count = 0
                    else:
                        self.l.support[0] = float('NaN')
                        count = 0
        else:
            self.l.support[0] = float('NaN')
            self.l.resistance[0] = float('NaN')