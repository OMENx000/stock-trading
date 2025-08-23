import yfinance as yf
from pprint import pprint

dat = yf.Ticker("RELIANCE.NS")
pprint(int(dat.info["industry"]))