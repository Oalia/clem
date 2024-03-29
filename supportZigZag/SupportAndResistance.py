import pandas as pd
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import yfinance as yahoo_finance
yahoo_finance.pdr_override()
from mpl_finance import candlestick2_ohlc
from argparse import ArgumentParser

parser = ArgumentParser(description='Algorithmic Support and Resistance')
parser.add_argument('-t', '--tickers', default='SPY500', type=str, required=False, help='Used to look up a specific tickers. Commma seperated. Example: MSFT,AAPL,AMZN default: List of S&P 500 companies')
parser.add_argument('-p', '--period', default='5d', type=str, required=False, help='Period to look back. valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. default: 1d')
parser.add_argument('-i', '--interval', default='1m', type=str, required=False, help='Interval of each bar. valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo. default: 1m')

parser.add_argument('-d', '--dif', default='0.05', type=float, required=False, help='Max %% difference between two points to group them together. Default: 0.05')
parser.add_argument('--time', default='1200', type=int, required=False, help='Max time measured in number of bars between two points to be grouped together. Default: 150')
parser.add_argument('-n', '--number', default='3', type=int, required=False, help='Min number of points in price range to draw a support/resistance line. Default: 3')
parser.add_argument('-m', '--min', default='150', type=int, required=False, help='Min number of bars from the start the support/resistance line has to be at to display chart. Default: 150')
args = parser.parse_args()

#S&P 500 Tickers
def getQuotes():
	if (args.tickers=="SPY500"):
		tickers = ['AMC','GOOG'] #'ABBV','ABMD','ACN','ATVI','ADBE','AMD','AAP','AES','AFL','A','APD','AKAM','ALK','ALB','ARE','ALXN','ALGN','ALLE','LNT','ALL','GOOGL','GOOG','MO','AMZN','AMCR','AEE','AAL','AEP','AXP','AIG','AMT','AWK','AMP','ABC','AME','AMGN','APH','ADI','ANSS','ANTM','AON','AOS','APA','AIV','AAPL','AMAT','APTV','ADM','ANET','AJG','AIZ','T','ATO','ADSK','ADP','AZO','AVB','AVY','BKR','BLL','BAC','BK','BAX','BDX','BRK-B','BBY','BIO','BIIB','BLK','BA','BKNG','BWA','BXP','BSX','BMY','AVGO','BR','BF-B','CHRW','COG','CDNS','CPB','COF','CAH','KMX','CCL','CARR','CAT','CBOE','CBRE','CDW','CE','CNC','CNP','CTL','CERN','CF','SCHW','CHTR','CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','KO','CTSH','CL','CMCSA','CMA','CAG','CXO','COP','ED','STZ','COO','CPRT','GLW','CTVA','COST','COTY','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','DISH','DG','DLTR','D','DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','ETFC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ETR','EOG','EFX','EQIX','EQR','ESS','EL','EVRG','ES','RE','EXC','EXPE','EXPD','EXR','XOM','FFIV','FB','FAST','FRT','FDX','FIS','FITB','FE','FRC','FISV','FLT','FLIR','FLS','FMC','F','FTNT','FTV','FBHS','FOXA','FOX','BEN','FCX','GPS','GRMN','IT','GD','GE','GIS','GM','GPC','GILD','GL','GPN','GS','GWW','HRB','HAL','HBI','HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HFC','HOLX','HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX','IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IPGP','IQV','IRM','JKHY','J','JBHT','SJM','JNJ','JCI','JPM','JNPR','KSU','K','KEY','KEYS','KMB','KIM','KMI','KLAC','KSS','KHC','KR','LB','LHX','LH','LRCX','LW','LVS','LEG','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT','L','LOW','LYB','MTB','MRO','MPC','MKTX','MAR','MMC','MLM','MAS','MA','MKC','MXIM','MCD','MCK','MDT','MRK','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MHK','TAP','MDLZ','MNST','MCO','MS','MOS','MSI','MSCI','MYL','NDAQ','NOV','NTAP','NFLX','NWL','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NBL','NSC','NTRS','NOC','NLOK','NCLH','NRG','NUE','NVDA','NVR','ORLY','OXY','ODFL','OMC','OKE','ORCL','OTIS','PCAR','PKG','PH','PAYX','PAYC','PYPL','PNR','PBCT','PEP','PKI','PRGO','PFE','PM','PSX','PNW','PXD','PNC','PPG','PPL','PFG','PG','PGR','PLD','PRU','PEG','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX','O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','NOW','SHW','SPG','SWKS','SLG','SNA','SO','LUV','SWK','SBUX','STT','STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TROW','TTWO','TPR','TGT','TEL','FTI','TDY','TFX','TXN','TXT','TMO','TIF','TJX','TSCO','TT','TDG','TRV','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA','UA','UNP','UAL','UNH','UPS','URI','UHS','UNM','VFC','VLO','VAR','VTR','VRSN','VRSK','VZ','VRTX','VIAC','V','VNO','VMC','WRB','WAB','WMT','WBA','DIS','WM','WAT','WEC','WFC','WELL','WST','WDC','WU','WRK','WY','WHR','WMB','WLTW','WYNN','XEL','XRX','XLNX','XYL','YUM','ZBRA','ZBH','ZION','ZTS']
	else:
		tickers = args.tickers.split(",")

	connected = False
	while not connected:
		try:
			ticker_df = web.get_data_yahoo(tickers, period = args.period, interval = args.interval)
			ticker_df = ticker_df.reset_index()
			connected = True
		except Exception as e:
			print("type error: " + str(e))
			time.sleep(5)
			pass
	return tickers, ticker_df



def drawTicker(ticker, ticker_df):
	"""Plots Resistance Support Line + Zigzag of Ticker
	
	Parameters
	----------
	ticker : str
		The current ticker 
	"""

	print("\n\n" + ticker)
	try:
		fig, ax = plt.subplots()
		# if(len(tickers)!=1):
		dfRes = createZigZagPoints(ticker, ticker_df.Close[ticker]).dropna()
		candlestick2_ohlc(ax,ticker_df['Open'][ticker],ticker_df['High'][ticker],ticker_df['Low'][ticker],ticker_df['Close'][ticker],width=0.6, colorup='g', colordown='r')
		# else:
		# 	dfRes = createZigZagPoints(ticker, ticker_df.Close).dropna()
		# 	candlestick2_ohlc(ax,ticker_df['Open'],ticker_df['High'],ticker_df['Low'],ticker_df['Close'],width=0.6, colorup='g', colordown='r')
		plt.plot(dfRes['Value'])

		# actual work after resistanceFinder is done
		ret = resistanceFinder(ticker, dfRes)

		x_max = ret
		if (x_max>args.min):
			plt.title(ticker)
			plt.show()
		plt.clf()
		plt.cla()
		plt.close()
	except Exception as e: print(e)

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
	"""

	minRetrace = minSegSize
	curVal = dfSeries[0]
	curPos = dfSeries.index[0]
	curDir = 1
	dfRes = pd.DataFrame(index=dfSeries.index, columns=["Dir", "Value"])
	for ln in dfSeries.index:
		if((dfSeries[ln] - curVal)*curDir >= 0):
			curVal = dfSeries[ln]
			curPos = ln
		else:	   
			retracePrc = abs((dfSeries[ln]-curVal)/curVal*100)
			if(retracePrc >= minRetrace):
				dfRes.loc[curPos, 'Value'] = curVal
				dfRes.loc[curPos, 'Dir'] = curDir
				appendToCSV(ticker+'ZigzagPoints.csv', [curVal, curDir])
				curVal = dfSeries[ln]
				curPos = ln
				curDir = -1*curDir
	return(dfRes)

def resistanceFinder(ticker, dfRes):
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
						if (index!=index2 and abs(index2-index)<args.time and row2.Dir==dir):
							if (abs((row.Value/row2.Value)-1)<(args.dif/100)):
									dropindexes.append(index2)
									values.append(row2.Value)
									if (index2<startx):
										startx = index2
									elif (index2>endx):
										endx = index2
									counter=counter+1

				if (counter>args.number):
					sum = 0
					print ("Support at ", end='')
					for i in range(len(values)-1):
						print("{:0.2f} and ".format(values[i]), end='')
					print("{:0.2f} \n".format(values[len(values)-1]), end='')
					removed_indexes.extend(dropindexes)
					for value in values:
						sum = sum + value
					if (endx>x_max):
						x_max=endx
					plt.hlines(y=sum/len(values), xmin=startx, xmax=endx, linewidth=1, color='r')
					# for real time/ historical purpose
					appendToCSV(ticker+"SupportResistanceDirection.csv", [sum/len(values), dir])
					ret = endx
		return ret
	except Exception as e: print(e)

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
	file = open(filename, 'a')
	writer = csv.writer(file)
	writer.writerow(data_point)
	file.close

while True:
	tickers, ticker_df = getQuotes()
	for ticker in tickers:
		drawTicker(ticker, ticker_df)
