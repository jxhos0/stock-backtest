# Overview
The following project was developed to back test a basic stock trading strategy for the Australian stock market by pulling data from the Yahoo Finance API. The idea behind it is that based on the inputted parameters, the strategy can be defined as successful or not over a large timeframe. 

More over, it quickly allows one to view the results of a bulk backtest and identify if the particular strategy works for one company more than others, allowing further investigation to take place.

## Process
At first a Jupyter Notebook file (back-test.ipynb) was created to download data for one ticker and analyse the results. It allowed dataframes to easily be modifed and displayed, making for fast optimisation of the code to view results. 

With the Jupyter Notebook file completed, a Python file (bulk-back-test.py) could then be implemented to quickly perform a bulk analysis of a list of tickers from the ASX50 (top 50 companies in Australia), by using the exact strategy used in back-test.ipynb. The result of running bulk-back-test.py is a pandas dataframe with columns labelled: Ticker, Winrate(%), AveProfit(%), AccGain(%). 

Viewing the printed dataframe allows for a quick and easy analysis of the strategy.

## Future Implementations
In the future I would like to modify the code to provide % outcomes for different profit levels, with a longer temr goal of implementing machine learning to modify and optimise the strategy.
