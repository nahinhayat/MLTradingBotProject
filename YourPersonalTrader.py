import pandas as pd
import streamlit as st
import numpy as np
import yfinance as yf
import hvplot.pandas
import hvplot as hv
hv.extension('bokeh', logo=False)
from prophet import Prophet
from datetime import datetime, timedelta

# Constants
SHORT_WINDOW = 5
LONG_WINDOW = 20
SHARE_SIZE = 500
INITIAL_CAPITAL = 1_000_000.0
TRADING_DAYS_PER_YEAR = 252
FORECAST_DAYS = 365
LOOKBACK_YEARS = 3

st.markdown("# Your Personal Trader")
st.markdown("## The ultimate trading tool for your investment")
st.markdown("### Use our trading algorithm to make the most calculated trades on the asset of your choice")


@st.cache_data
def fetch_data(ticker, start, end):
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end).drop(columns=["Open", "High", "Low", "Volume"])
    df.index.names = ["timestamp"]
    return df


@st.cache_data
def run_prophet(ticker, start, end):
    t = yf.Ticker(ticker)
    ts_df = t.history(start=start, end=end).loc[:, ["Close"]]
    ts_df.index = ts_df.index.strftime("%Y-%m-%d %H:%M:%S")
    ts_reset_df = ts_df.reset_index()
    ts_reset_df.columns = ["ds", "y"]
    m = Prophet()
    m.fit(ts_reset_df)
    future = m.make_future_dataframe(periods=FORECAST_DAYS, freq="D")
    forecast = m.predict(future)
    return forecast.loc[:, ["ds", "yhat"]]


ticker_input = st.text_input("Enter the ticker for your stock of choice")

if ticker_input.strip():
    try:
        today = datetime.now()
        start_day = today - timedelta(days=LOOKBACK_YEARS * 365)

        asset_df = fetch_data(ticker_input, start_day, today)

        if asset_df.empty:
            st.error(f"No data found for ticker '{ticker_input}'. Please check the symbol and try again.")
            st.stop()

        # SMA signals
        asset_df["SMA_Fast"] = asset_df["Close"].rolling(window=SHORT_WINDOW).mean()
        asset_df["SMA_Slow"] = asset_df["Close"].rolling(window=LONG_WINDOW).mean()
        asset_df["Signal"] = 0.0
        asset_df.loc[asset_df.index[SHORT_WINDOW:], "Signal"] = np.where(
            asset_df["SMA_Fast"].iloc[SHORT_WINDOW:] > asset_df["SMA_Slow"].iloc[SHORT_WINDOW:], 1.0, 0.0
        )
        asset_df["Entry/Exit"] = asset_df["Signal"].diff()

        # Simulated portfolio
        asset_df["Position"] = SHARE_SIZE * asset_df["Signal"]
        asset_df["Entry/Exit Position"] = asset_df["Position"].diff()
        asset_df["Portfolio Holdings"] = asset_df["Close"] * asset_df["Position"]
        asset_df["Portfolio Cash"] = INITIAL_CAPITAL - (asset_df["Close"] * asset_df["Entry/Exit Position"]).cumsum()
        asset_df["Portfolio Total"] = asset_df["Portfolio Cash"] + asset_df["Portfolio Holdings"]
        asset_df["Portfolio Daily Returns"] = asset_df["Portfolio Total"].pct_change()
        asset_df["Portfolio Cumulative Returns"] = (1 + asset_df["Portfolio Daily Returns"]).cumprod() - 1

        annualized_return = round(asset_df["Portfolio Daily Returns"].mean() * TRADING_DAYS_PER_YEAR, 4)
        cumulative_return = round(asset_df["Portfolio Cumulative Returns"].iloc[-1], 4)
        annual_vol = round(asset_df["Portfolio Daily Returns"].std() * np.sqrt(TRADING_DAYS_PER_YEAR), 4)

        total_portfolio_value = asset_df[["Portfolio Total"]].hvplot(
            line_color="lightgray",
            ylabel="Total Portfolio Value",
            xlabel="Date",
            width=1000,
            height=400,
        )

        # Prophet forecast for entry/exit signals
        forecast = run_prophet(ticker_input, start_day, today)
        buy_or_sell_df = forecast.copy()
        buy_or_sell_df.columns = ["Date", "Close"]
        buy_or_sell_df["SMA_Fast"] = buy_or_sell_df["Close"].rolling(window=SHORT_WINDOW).mean()
        buy_or_sell_df["SMA_Slow"] = buy_or_sell_df["Close"].rolling(window=LONG_WINDOW).mean()
        buy_or_sell_df["Signal"] = 0.0
        buy_or_sell_df.loc[buy_or_sell_df.index[SHORT_WINDOW:], "Signal"] = np.where(
            buy_or_sell_df["SMA_Fast"].iloc[SHORT_WINDOW:] > buy_or_sell_df["SMA_Slow"].iloc[SHORT_WINDOW:], 1.0, 0.0
        )
        buy_or_sell_df["Entry/Exit"] = buy_or_sell_df["Signal"].diff()
        buy_or_sell_df = buy_or_sell_df.dropna()
        buy_or_sell_df.set_index("Date", inplace=True)

        current_date = datetime.now().strftime("%Y-%m-%d")
        next_point_df = buy_or_sell_df.loc[current_date:]

        buy_signals = next_point_df.loc[next_point_df["Entry/Exit"] == 1.0]
        sell_signals = next_point_df.loc[next_point_df["Entry/Exit"] == -1.0]
        next_point_buy = round(buy_signals["Close"].values[0], 2) if not buy_signals.empty else None
        next_point_buy_date = buy_signals.index[0] if not buy_signals.empty else None
        next_point_sell = round(sell_signals["Close"].values[0], 2) if not sell_signals.empty else None
        next_point_sell_date = sell_signals.index[0] if not sell_signals.empty else None

        st.write(
            f"If the trading algorithm we have created was used with {ticker_input} for the last three years, "
            f"there would be cumulative returns yielding {round(cumulative_return * 100, 2)}%, "
            f"an annualized return of {round(annualized_return * 100, 2)}%, "
            f"with a volatility of {round(annual_vol * 100, 2)}%."
        )

        if st.button("Display graph of a portfolio's value using our trading strategy over last three years with this stock"):
            st.write(hv.render(total_portfolio_value, backend="bokeh"))

        investment_input = st.text_input("How much would you like to invest?")
        if investment_input.strip():
            try:
                investment_amount_float = float(investment_input)
            except ValueError:
                st.error("Please enter a valid number for the investment amount.")
                st.stop()

            st.write(
                f"The average possible returns for the next year would be "
                f"\\${round(annualized_return * investment_amount_float, 2)}. "
                f"With possible maximum returns as high as "
                f"\\${round((annualized_return + annual_vol) * investment_amount_float, 2)} "
                f"but possible maximum losses as low as "
                f"${round((annualized_return - annual_vol) * investment_amount_float, 2)}"
            )

            if st.button("Find next price for entry"):
                if next_point_buy is not None:
                    st.write(f"When the price for {ticker_input} hits ${next_point_buy}, this will be the time to buy. This should happen around {next_point_buy_date}")
                else:
                    st.write("No upcoming buy signal found in the forecast period.")

            if st.button("Find next price for exit"):
                if next_point_sell is not None:
                    st.write(f"When the price for {ticker_input} hits ${next_point_sell}, this will be the time to sell. This should happen around {next_point_sell_date}")
                else:
                    st.write("No upcoming sell signal found in the forecast period.")

    except Exception as e:
        st.error(f"An error occurred while processing '{ticker_input}': {e}")
