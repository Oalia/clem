import backtrader.indicator as btind



class AvgRelTime(btind):
    lines = ('avgToTime')

    def __init__(self):

        self.cum_data = btind.Accum(self.data)
        self.count = self.count + 1
        self.average_reltive_time = self.cum_data / self.count


        self.lines.avgToTime = self.average_reltive_time