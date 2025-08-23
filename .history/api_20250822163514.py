import yfinance as yf
import time
from pprint import pprint

now = time.time() 
dat = yf.Ticker("AAPL")
pprint(dat.fast_info["last_price"])
#pprint(dat.info["currentPrice"])
print(time.time() - now)
