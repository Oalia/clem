##+------------------------------------------------------------------+
## Copyright (C) 2019 Nikolai Khramkov
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##+------------------------------------------------------------------+


import backtrader as bt

class ZigZag(bt.ind.PeriodN):
    '''
      ZigZag indicator.
    '''
    lines = (
        'trend',
        'last_high',
        'last_low',
        'zigzag',
    )

    plotinfo = dict(
        subplot=False,
        plotlinelabels=True, plotlinevalues=True, plotvaluetags=True,
    )

    plotlines = dict(
        trend=dict(_plotskip=True),
        last_high=dict(color='green', ls='-', _plotskip=True),
        last_low=dict(color='black', ls='-', _plotskip=True),
        zigzag=dict(_name='zigzag', color='blue', ls='-', _skipnan=True),
    )

    params = (
        ('period', 2),
        ('retrace', 0.05), # in percent
        ('minbars', 2), # number of bars to skip after the trend change
    )

    def __init__(self):
        super(ZigZag, self).__init__()

        assert self.p.retrace > 0, 'Retracement should be above zero.'
        assert self.p.minbars >= 0, 'Minimal bars should be >= zero.'

        self.ret = self.data.close * self.p.retrace / 100
        self.minbars = self.p.minbars
        self.count_bars = 0
        self.last_pivot_t = 0
        self.last_pivot_ago = 0

    def prenext(self):
        self.l.trend[0] = 0
        self.l.last_high[0] = self.data.high[0]
        self.l.last_low[0] = self.data.low[0]
        self.l.zigzag[0] = (self.data.high[0] + self.data.low[0]) / 2

    def next(self):
        curr_idx = len(self.data)
        self.ret = self.data.close[0] * self.p.retrace / 100
        self.last_pivot_ago = curr_idx - self.last_pivot_t
        self.l.trend[0] = self.l.trend[-1]
        self.l.last_high[0] = self.l.last_high[-1]
        self.l.last_low[0] = self.l.last_low[-1]
        self.l.zigzag[0] = float('nan')

        # Search for trend
        if self.l.trend[-1] == 0:
            if self.l.last_low[0] < self.data.low[0] and self.l.last_high[0] < self.data.high[0]:
                self.l.trend[0] = 1
                self.l.last_high[0] = self.data.high[0]
                self.last_pivot_t = curr_idx

            elif self.l.last_low[0] > self.data.low[0] and self.l.last_high[0] > self.data.high[0]:
                self.l.trend[0] = -1
                self.l.last_low[0] = self.data.low[0]
                self.last_pivot_t = curr_idx

        # Up trend
        elif self.l.trend[-1] == 1:
            if self.data.high[0] > self.l.last_high[-1]:
                self.l.last_high[0] = self.data.high[0]
                self.count_bars = self.minbars
                self.last_pivot_t = curr_idx

            elif self.count_bars <= 0 and self.l.last_high[0] - self.data.low[0] > self.ret and self.data.high[0] < self.l.last_high[0]:
                self.l.trend[0] = -1
                self.count_bars = self.minbars
                self.l.last_low[0] = self.data.low[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_high[0]
                self.last_pivot_t = curr_idx

            elif self.count_bars < self.minbars and self.data.close[0] < self.l.last_low[0]:
                self.l.trend[0] = -1
                self.count_bars = self.minbars
                self.l.last_low[0] = self.data.low[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_high[0]
                self.last_pivot_t = curr_idx

        # Down trend
        elif self.l.trend[-1] == -1:
            if self.data.low[0] < self.l.last_low[-1]:
                self.l.last_low[0] = self.data.low[0]
                self.count_bars = self.minbars
                self.last_pivot_t = curr_idx

            elif self.count_bars <= 0 and self.data.high[0] - self.l.last_low[0] > self.ret and self.data.low[0] > self.l.last_low[0]:
                self.l.trend[0] = 1
                self.count_bars = self.minbars
                self.l.last_high[0] = self.data.high[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_low[0]
                self.last_pivot_t = curr_idx

            elif self.count_bars < self.minbars and self.data.close[0] > self.l.last_high[-1]:
                self.l.trend[0] = 1
                self.count_bars = self.minbars
                self.l.last_high[0] = self.data.high[0]
                self.l.zigzag[-self.last_pivot_ago] = self.l.last_low[0]
                self.last_pivot_t = curr_idx

        # Decrease minbars counter
        self.count_bars -= 1