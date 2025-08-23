import yfinance as yf
import time
from pprint import pprint

now = time.time() 
dat = yf.Ticker("MSFT")
pprint(dat.info["currentPrice"])
print(time.time() - now)

#pprint(dat.fast_info["last_price"])