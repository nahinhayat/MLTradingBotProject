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
from prophet import Prophet
import datetime as dt

st.markdown("# The Ultimate Trading Tool")
st.markdown("## Find out which stock is best for your investment")


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
        short_window = 3
        long_window = 50
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
        annualized_return = round((asset_df['Portfolio Daily Returns'].mean() * 252), 4)
    #calc cumulative returns
        cumulative_return = round((asset_df["Portfolio Cumulative Returns"][-1]), 4)
    #calc annual volatility
        annual_vol = round(((asset_df['Portfolio Daily Returns'].std() * np.sqrt(252))), 4)
    # Visualize the value of the total portfolio
        total_portfolio_value = asset_df[['Portfolio Total']].hvplot(
            line_color='lightgray',
            ylabel='Total Portfolio Value',
            xlabel='Date',
            width=1000,
            height=400)
    #build model to forecast future prices of stock
    #create time series dataframe
        ts_df = starter_ticker.history(period="1d", start= start_day, end=today).loc[:, ["Close"]]
        ts_df.index = ts_df.index.strftime("%Y-%m-%d %H:%M:%S")
        ts_reset_df = ts_df.reset_index()
        ts_reset_df.columns = ["ds","y"]
    #start Prophet forecast
        m = Prophet()
        m.fit(ts_reset_df)
        future = m.make_future_dataframe(periods = 365, freq = "D")
        forecast = m.predict(future)
        forecast = forecast.loc[:, ["ds","yhat"]]
    #create dataframe to find next signal and entryexit points
        buy_or_sell_df = forecast
        buy_or_sell_df.columns = ["Date","Close"]
    #create columns for needed data
        buy_or_sell_df["SMA_Fast"] = buy_or_sell_df['Close'].rolling(window=short_window).mean()
        buy_or_sell_df["SMA_Slow"] = buy_or_sell_df['Close'].rolling(window=long_window).mean()
        buy_or_sell_df["Signal"] = 0.0
        buy_or_sell_df["Signal"][short_window:] = np.where(
        buy_or_sell_df["SMA_Fast"][short_window:] > buy_or_sell_df["SMA_Slow"][short_window:], 1.0, 0.0
        )
        buy_or_sell_df["Entry/Exit"] = buy_or_sell_df["Signal"].diff()
        buy_or_sell_df.dropna()
        buy_or_sell_df.set_index('Date', inplace = True)
    #create dataframe with only future values
        current_date = datetime.now().strftime("%Y-%m-%d")
        next_point_df = buy_or_sell_df.loc[current_date:]
    #find next point which indicated to buy
        search_value_buy = 1.0
        next_point_buy = round(next_point_df.loc[next_point_df["Entry/Exit"] == search_value_buy, "Close"].values[0], 2)
        next_point_buy_date = next_point_df.loc[next_point_df["Entry/Exit"] == search_value_buy].index[0]
    #find next point to sell
        search_value_sell = -1.0
        next_point_sell = round(next_point_df.loc[next_point_df["Entry/Exit"] == search_value_sell, "Close"].values[0], 2)
        next_point_sell_date = next_point_df.loc[next_point_df["Entry/Exit"] == search_value_sell].index[0]
    #display info 
        st.write(f"If the trading alogirthm we have created was used with {ticker_input} for the last three years, there would be cumulative returns yielding {cumulative_return *100}%, an annualized return of {annualized_return *100}%, with a volatility of {round((annual_vol *100),2)}%.")
        

#display button to show visualization of sim portfolio
if ticker_input.strip():
    if st.button("Display graph of a portfolio's value using our trading strategy over last three years with this stock"):
        st.write(hv.render(total_portfolio_value, backend='bokeh'))
        

#create input for investment amount        
if ticker_input.strip():
    investment_input = st.text_input("How much would you like to invest?")
    if investment_input.strip():
        investment_amount_float = float(investment_input)
        st.write(f"The average possible returns for the next year would be \\${round((annualized_return*investment_amount_float), 2)}. With possible maximum returns as high as \\${round(((annualized_return+annual_vol)*investment_amount_float), 2)} but possible maximum losses as low as ${round(((annualized_return-annual_vol)*investment_amount_float), 2)}")
        if investment_input.strip():
            if st.button("Find next price for entry"):
                st.write(f"When the price for {ticker_input} hits ${next_point_buy}, this will be the time to buy. This should happen around {next_point_buy_date}")
        if investment_input.strip():
            if st.button("Find next price for exit"):
                st.write(f"When the price for {ticker_input} hits ${next_point_sell}, this will be the time to sell. This should happen around {next_point_sell_date}")
    
            
            
