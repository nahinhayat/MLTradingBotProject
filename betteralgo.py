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
from datetime import datetime, timedelta
import hvplot.pandas
import hvplot as hv
hv.extension('bokeh', logo=False)
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import ColumnDataSource

st.markdown("# The Ultimate Trading Tool")
st.markdown("## Find out which stock is best for your investment and when to buy/sell ")


#get ticker imput from user
ticker_input = st.text_input("Enter the ticker for your stock of choice")

#after ticker is entered by user run the algo
if ticker_input.strip():
    #import stock close price
        today = datetime.now()
        start_day = today - timedelta(days=3*365)
        starter_ticker = yf.Ticker(ticker_input)
        asset_df = starter_ticker.history(period="1d", start= start_day, end=today).drop(columns=["Open", "High","Low","Volume"])
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
    #calc cumulative returns
        cumulative_return = asset_df["Portfolio Cumulative Returns"][-1]
    #calc annual volatility
        annual_vol = asset_df['Portfolio Daily Returns'].std() * np.sqrt(252)
    # Visualize the value of the total portfolio
        total_portfolio_value = asset_df[['Portfolio Total']].hvplot(
            line_color='lightgray',
            ylabel='Total Portfolio Value',
            xlabel='Date',
            width=1000,
            height=400)

#display button to show visualization of sim portfolio
if ticker_input.strip():
    if st.button("Display graph of a portfolio's value using our trading strategy over last three years with this stock"):
        st.write(hv.render(total_portfolio_value, backend='bokeh'))
        

#display button for annualized return after ticker input
if ticker_input.strip():
    if st.button("Display annualized return for last three years"):
        st.write((annualized_return *100))
        
#display button for cumulative returns after ticker input
if ticker_input.strip():
    if st.button("Display cumulative returns for last three years"):
        st.write((cumulative_return *100))
        
#display button for annual volatility after ticker input
if ticker_input.strip():
    if st.button("Display annual volatility for last three years"):
        st.write((annual_vol *100))

if ticker_input.strip():
    investment_input = st.text_input("How much would you like to invest?")
    if investment_input.strip():
        investment_amount_float = float(investment_input)
        if st.button("Calculate your average possible returns for the next year"):
            st.write((annualized_return *investment_amount_float))
        if st.button("Calculate the maximum possible returns") :
            st.write((annualized_return+annual_vol)*investment_amount_float)
        if st.button("Calculate maximum possible losses") :
            st.write((annualized_return-annual_vol)*investment_amount_float)
            
