import yfinance as yf
from pprint import pprint

dat = yf.Ticker("RELIANCE.NS")
pprint(dat.fast_info["last_price"])