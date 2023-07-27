Your Personal Trader Project

Description of code:

This project is a web application run through Streamlit which allows users to use the stock or crypto or their choice with a trading algorithm I have created. They can see how the stock they choose has performed historically with the strategy integrated in the algorithm, they are given evaluation metrics such as cumulative returns, annualized returns, and annual volatility. Then they are also given the option to input an amount if they are interested in investing and find the possible returns for the next year using the algorithm.  If the user is interested in using the strategy after seeing this information, I have a model which can forecast the next time to buy or if they are already using the strategy, when to sell.

Details:

The libraries and functions that need to be imported are showcased here:

![screenshot1](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot1.png)

Now the first step to get the application working is to import the stock price information we need from the Yahoo Finance API. We will be needing the last three year's of closing prices and have to find a way to make sure the information stays up to date and that we can import any stock the user inputs. This is done by creating a text input to recieve the ticker name from the user plus creating variables set to today's date and the date three years ago. We then use these variables when creating the DataFrame with the API. 

![screenshot2](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot2.png)

The next step is to create columns in the DataFrame to hold the SMAs, trade signals, and entry/exit points to be used in the trading algorithm:

![screenshot3](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot3.png)

This allows us to backtest the algorithm against whichever stock the user has inputted using a simulated portfolio. We calculate evaluation metrics using this simulation and also create a graph of the portfolio's value over time for the user to analyze.

![screenshot4](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot4.png)

After the algorithm has been run, we are tasked with predicting the next signal to enter or exit. This is done by creating a new DataFrame and importing only the closing prices for the stock from the last three years, then use Prophet to forecast future values for the closing values, and finally do the same process we did with the algorithm to find the entry/exit signals in this DataFrame:

![screenshot5](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot5.png)

This completes the code for running the models, we place all this code inside an if statement for Streamlit, which will result in the models being run after the user inputs the name of the ticker, and displays the evaluation metrics: 

![screenshot6](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot6.png)

Then to complete the code we have if statements for each button that returns information to the user after inputting their desired investment amount, such as the possible returns and next entry/ exit point

![screenshot7](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot7.png)

Example of Streamlit Application Experience:

Upon first running the application the user is prompted to enter the ticker for the stock they are interested in:

![screenshot8](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot8.png)

After entering the ticker, they are given the evaluation metrics and are able to view the graph of a portfolio utilizing the alogirthm for the last three years. Then they are prompted to enter an amount they would like to invest:

![screenshot9](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot9.png)

Finally, when given the invesment amount, the user is given the possible returns for the next year and can view the next entry or exit position:

![screenshot10](https://github.com/nahinhayat/MLTradingBotProject/blob/main/screenshots/screenshot10.png)

Author: Nahin Hayat https://www.linkedin.com/in/nahinhayat/