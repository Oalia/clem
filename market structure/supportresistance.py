# import backtrader as bt
# import backtrader.indicators as btind
# import backtrader.feeds as btfeeds
# import pandas as pd
# from csv import writer
# from nullfilter import NullBarFilter


# class SupRes(bt.ind.PeriodN):
#     """
#     Support Resistance
#     takes in zig zag feed. Returns support resistance line feed

#     for each entry in the feed, it should return nan for entry if 
#         no support resistance is found.
#     Else it should return sup_res, and direction for that time feed.

#     Our external file helps us run the process. 
#     """
#     lines = (
#         'sup_res',
#         'direction' #? is it possible to have direction(support or resist) as boolean
#     )
#     params = (('backwards', 6), ('dif', 250), ('number', 3))\

#     plotinfo = dict(
#         subplot=False,
#         plotlinelabels=True, plotlinevalues=True, plotvaluetags=True,
#     )

#     plotlines = dict(
#         sup_res=dict(_name='sup_res', color='red', ls='-', _skipnan=True, ),
#     )

#     def __init__(self):
#         ""
#         self.data = self.data.addfilter(NullBarFilter)

#          # this works. It is going to get beautiful right now
    
#     def next(self):
#         self.df = pd.read_csv("zigzags.csv")

#         # removing self.dres to just dres
#         # self.data refers to our input data feed which is of the zigzag class
#         if self.data.l.zigzag > 0:
#             if self.df.empty:
#                 entry = {'Pivot': self.data.l.zigzag[0], 'Value': self.data.l.value[0]}
#                 self.df = self.df.append(entry, ignore_index = True)
#                 self.df.to_csv('zigzags.csv', mode='a')
#             else:
#                 # try:
#                     counter = 0
#                     max_counter = 0 # most lookbacks
#                     seen_res = []
#                     sum = 0
#                     start = 1
#                     rev_df = self.df.iloc[::-1]
#                     for row in rev_df.itertuples():
#                         # if counter < self.params.backwards:
#                         #     counter = counter+1
#                         print(row)
#                     # for idx in reversed(self.df.index):
#                     #     if counter < self.params.backwards:
#                     #         counter = counter+1
#                     #         if self.df.iloc[idx]["Value"] - self.data.l.value[0] == 0:
#                     #             if (abs((self.data.l.zigzag[0]/self.df.Pivot[idx])-1) < (self.params.dif/100)):
#                     #                 seen_res.append(self.df.Pivot[idx])
#                     #                 self.df = self.df.drop(idx)

#                     if (len(seen_res) > 2):           
#                         for x in seen_res:
#                             print(x)
#                             sum = sum + x
#                         print(len(seen_res))
#                         resistance = sum/len(seen_res)
#                         resist_or_support_dir =  self.data.l.value[0]

#                         entry = [ resistance, resist_or_support_dir ]

#                         with open('support_resistance.csv', 'a') as f_object:
#                             writer_object = writer(f_object)
#                             writer_object.writerow(entry)
#                             f_object.close()
#                     # self.df.to_csv("zigzags.csv")

#                 # except Exception as e:
#                     # print(e)