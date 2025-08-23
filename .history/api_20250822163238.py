import yfinance as yf
import time
from pprint import pprint

now = time.time() 
dat = yf.Ticker("RELIANCE.NS")
pprint(dat.info["current_price"])
print(time.time() - now)