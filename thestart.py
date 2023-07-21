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

#import stock close price
ticker_input = st.text_input("Enter the ticker for your stock of choice")
today = date.today()
starter_ticker = yf.Ticker(ticker_input)
asset_df = starter_ticker.history(period="1d", start="2000-01-01", end=today).drop(columns=["Open", "High","Low","Volume"])
asset_df.index.names = ["timestamp"]

#add Actual Returns column
asset_df["Actual Returns"] = asset_df["Close"].pct_change()

#create columns for SMA_fast and SMA_slow
short_window = 4
long_window = 100
asset_df["SMA_Fast"] = asset_df['Close'].rolling(window=short_window).mean()
asset_df["SMA_Slow"] = asset_df['Close'].rolling(window=long_window).mean()

#create signal column
asset_df['Signal'] = 0.0
asset_df.loc[(asset_df['Actual Returns'] >= 0), 'Signal'] = 1
asset_df.loc[(asset_df['Actual Returns'] < 0), 'Signal'] = -1

#create feature and target sets
X = asset_df[['SMA_Fast', 'SMA_Slow']].shift().dropna()
y = asset_df['Signal']

#create X and y train DataFrames
training_begin = "2000-05-25 00:00:00-04:00"
training_end =  "2018-05-25 00:00:00-04:00"
X_train = X.loc[training_begin:training_end]
y_train = y.loc[training_begin:training_end]

#create test DataFrames
X_test = X.loc["2018-05-29 00:00:00-04:00":]
y_test = y.loc["2018-05-29 00:00:00-04:00":]

#scale the features
scaler = StandardScaler()
X_scaler = scaler.fit(X_train)
X_train_scaled = X_scaler.transform(X_train)
X_test_scaled = X_scaler.transform(X_test)

#use SCV model
svm_model = svm.SVC()
svm_model = svm_model.fit(X_train_scaled, y_train)
svm_pred = svm_model.predict(X_test_scaled)

#review class report from model predictions
svm_testing_report = classification_report(y_test, svm_pred)

accuracy = accuracy_score(y_test, svm_pred)
if st.button("Display the accuracy of the trading algo with this Stock"):
    st.write(accuracy)