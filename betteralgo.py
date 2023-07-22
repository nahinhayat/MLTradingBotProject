#imports
import pandas as pd
import requests
import json
import streamlit as st
import numpy as np
import yfinance as yf
from datetime import date
import streamlit as st
from pandas.tseries.offsets import DateOffset
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

#get ticker imput from user
ticker_input = st.text_input("Enter the ticker for your stock of choice")

#after ticker is entered by user run the algo
if ticker_input.strip():
    #import stock close price
        today = date.today()
        starter_ticker = yf.Ticker(ticker_input)
        asset_df = starter_ticker.history(period="1d", start="2000-01-01", end=today).drop(columns=["Open", "High","Low","Volume"])
        asset_df.index.names = ["timestamp"]
    #create columns for SMA windows
        short_window = 4
        long_window = 30
        asset_df["SMA_Fast"] = asset_df['Close'].rolling(window=short_window).mean()
        asset_df["SMA_Slow"] = asset_df['Close'].rolling(window=long_window).mean()
    #create column to hold trading signal
        asset_df["Signal"] = 0.0
        asset_df["Signal"][short_window:] = np.where(
                asset_df["SMA_Fast"][short_window:] > asset_df["SMA_Slow"][short_window:], 1.0, 0.0
        )
    #add column for entry/exit
        asset_df["Entry/Exit"] = asset_df["Signal"].diff()
    #create sim portfolio
        initial_capital = float(1000000)
        share_size = 500
        asset_df["Position"] = share_size * asset_df["Signal"]
        asset_df["Entry/Exit Position"] = asset_df["Position"].diff()
        asset_df["Portfolio Holdings"] = asset_df["Close"] * asset_df["Position"]
        asset_df["Portfolio Cash"] = initial_capital - (asset_df["Close"]*asset_df["Entry/Exit Position"]).cumsum()
        asset_df["Portfolio Total"] = asset_df["Portfolio Cash"] + asset_df["Portfolio Holdings"]
        asset_df["Portfolio Daily Returns"] = asset_df["Portfolio Total"].pct_change()
        asset_df["Portfolio Cumulative Returns"] = (1+ asset_df["Portfolio Daily Returns"]).cumprod()-1
    #calc annualized return
        annualized_return = asset_df['Portfolio Daily Returns'].mean() * 252
    
#display button for annualized return after ticker input
if ticker_input.strip():
    if st.button("Display annualized return"):
        st.write((annualized_return *100))




