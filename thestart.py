#imports
import pandas as pd
import requests
import json
import streamlit as st
import numpy as np
import yfinance as yf
from datetime import date
import streamlit as st

#import ticker data
ticker_input = st.text_input("Enter the ticker for your stock of choice")
today = date.today()
starter_ticker = yf.Ticker("ticker_input")
asset_close_df = starter_ticker.history(period="1d", start="2000-01-01", end=today).drop(columns=["Open", "High","Low","Volume"])
asset_close_df.index.names = ["timestamp"]
asset_close_df = pd.concat([asset_close_df], axis=1, keys=["S&P500"])

if st.button("Display Close Price"):
    st.write(asset_close_df.tail())