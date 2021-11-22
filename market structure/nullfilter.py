
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


__all__ = ['NullBarFilter']


class NullBarFilter(object):
    '''Modify the data stream to remove bars that are null by checking if the trend is between -1 and 1

    Params:

      - ``size`` (default: *None*) The size to consider for each brick

    See:
      - http://stockcharts.com/school/doku.php?id=chart_school:chart_analysis:renko

    '''

    def __init__(self, data):
        pass
        
    def __call__(self, data):
        
        if (data[0] >= 0):
            return False  # length of data stream is unaltered

        data.backwards()
        return True  # length of stream was changed, get new bar
 