import requests
import yfinance as yf


url = "https://yfapi.net/v6/finance/chart"
# def buildUrl(symbols):
#     symbol_list = ','.join([symbol for symbol in symbols])

querystring = {"symbols":"AAPL,BTC-USD,EURUSD=X"}

headers = {
    'x-api-key': "xrDuCavpD84Cr6b3JbP2F4mt38PghaM01KiYpZiJ"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)