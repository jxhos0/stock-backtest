import yfinance as yf
import pandas as pd
import numpy as np


pd.options.mode.chained_assignment = None
# Set the ticket value, start date (in 'YYYY-MM-DD' format) and the data 
# interval (options '1d' or '1wk')
startDate = '2015-01-01'
interval = '1wk'

# Set the desired take profit and stop loss percentages
profitTargetPercentage = 10
allowedLossPercentage = 5


def backtest(df):
    # Create a copy of the original dataframe and delete the Adjusted Close and Volume columns
    mod_df = df.copy().drop(columns=['Adj Close', 'Volume'])

    # Calculate the 20 EMA and 40 EMA for later conditional checks
    mod_df['EMA20'] = mod_df.Close.ewm(span=20, adjust=False).mean()
    mod_df['EMA40'] = mod_df.Close.ewm(span=40, adjust=False).mean()

    # Calculate the MACD and Signal for later conditional checks
    exp1 = mod_df.Close.ewm(span=3, adjust=False).mean()
    exp2 = mod_df.Close.ewm(span=10, adjust=False).mean()
    mod_df['MACD'] = (exp1 - exp2)
    mod_df['MACD GRAD'] = mod_df.MACD.diff() 
    mod_df['Signal'] = mod_df.MACD.ewm(span=16, adjust=False).mean()

    # Remove any NaN values
    mod_df.dropna(inplace=True)


    # Create new columns for the dataframe for buy signals, sell signals, buy price, 
    # sell price and a transaction mumber

    # Display a buy signal with a 1 if conditions are met, otherwise display 0
    mod_df['BuySignal'] = np.where((mod_df.Close > mod_df.EMA40) & (mod_df.MACD > 0) & (mod_df.MACD > mod_df.Signal), 1, 0) 
    mod_df['SellSignal'] = np.where((mod_df.Close < mod_df.EMA40), 1, 0)
    mod_df['BuyPrice'] = None
    mod_df['SellPrice'] = None
    mod_df['TransactionNumber'] = None

    # Create a copy of the modified dataframe and drop the indicator columns 
    # as they are no longer needed
    mod_df_with_signals = mod_df.copy().drop(columns=['EMA20', 'EMA40', 'MACD', 'MACD GRAD', 'Signal'])

    # Set a bought and transaction number variable
    bought = False
    transaction = 0

    # Loop over each row in the modified dataframe with signals
    for i in range(0, len(mod_df_with_signals)):
        # Check that a position is not already held with the stock
        if not bought:
            # If a buy signal is present
            if mod_df_with_signals.BuySignal.iloc[i]:
                # Set the buy price to the close of the row and update the dataframe with the purchase price
                buyPrice = mod_df_with_signals.Close.iloc[i]
                mod_df_with_signals.BuyPrice.iloc[i] = buyPrice

                # Set the transaction number as a string with leading zeros
                mod_df_with_signals.TransactionNumber.iloc[i] = str("{:05d}".format(transaction))

                # Toggle the bought variable to true
                bought = True  

                # Set the desired take profit and stop loss prices
                TP = buyPrice * (1 + profitTargetPercentage / 100)
                SL = buyPrice * (1 - allowedLossPercentage / 100)
        
        # If a position is already held on the stock
        else:
            # If there is not a sell signal
            if not mod_df_with_signals.SellSignal.iloc[i]:
                # Check if the open, high, low or close price is equal to or greater than the take profit
                if ((mod_df_with_signals.Open.iloc[i] >= TP) | (mod_df_with_signals.High.iloc[i] >= TP) | (mod_df_with_signals.Low.iloc[i] >= TP) | (mod_df_with_signals.Close.iloc[i] >= TP)):
                    # Set the sell price to the close of the row and update the dataframe with the sell price
                    mod_df_with_signals.SellPrice.iloc[i] = TP
                    mod_df_with_signals.TransactionNumber.iloc[i] = str("{:05d}".format(transaction))

                    # Toggle the bought variable to false
                    bought = False

                    # Increment the transaction number
                    transaction += 1
            
            # If a sell signal is present
            else:
                # Set the sell price to the stop loss and update the dataframe with the sell price
                mod_df_with_signals.SellPrice.iloc[i] = SL
                mod_df_with_signals.TransactionNumber.iloc[i] = str("{:05d}".format(transaction))

                # Toggle the bought variable to false
                bought = False

                # Increment the transaction number
                transaction += 1


    # Group the dataframe with purchases and sells by the transaction number
    df_grouped_transaction = mod_df_with_signals[~mod_df_with_signals['TransactionNumber'].isnull()]
    df_grouped_transaction = df_grouped_transaction[['BuyPrice', 'SellPrice', 'TransactionNumber']].copy()
    df_grouped_transaction.set_index('TransactionNumber', inplace=True)
    df_grouped_transaction = df_grouped_transaction.groupby(level=0).max()

    # Drop NaN values to handle any positions at the end that may not be sold
    df_grouped_transaction.dropna(inplace=True)

    # Create a profits dataframe and calculate the profit from each transaction pair as a percentage
    df_profits = pd.DataFrame(columns=['Profit'])
    df_profits['Profit'] = (df_grouped_transaction.SellPrice - df_grouped_transaction.BuyPrice) / df_grouped_transaction.BuyPrice

    # Function to calculate and return the winrate, average profit and the % gain
    def analyse(array):
        winrate = len(array[array.Profit > 0]) / len(array) * 100 if len(array) > 0 else 0
        aveProfit = array.Profit.mean() * 100
        gain = (array.Profit + 1).cumprod()[-1] if (array.Profit + 1).cumprod()[-1] > 1 else -(1 - (array.Profit + 1).cumprod()[-1])

        return winrate, aveProfit.round(decimals=2),round(gain * 100, 2)
    # Analyse the profits data frame and save the results

    return analyse(df_profits)

# Download table of companies
companies_table = pd.read_html('https://en.wikipedia.org/wiki/S%26P/ASX_50')[0]

# Create a list of company tickers
tickers = companies_table['Symbol']
tickers.to_list()
tickers = [ticker + '.AX' for ticker in tickers]

# Create a dataframe to store results
df_outcome = pd.DataFrame(columns=['Ticker', 'Winrate(%)', 'AveProfit(%)', 'AccGain(%)'])

# Loop through list of tickers and backtest the data
for ticker in tickers:
    df = yf.download(ticker, start=startDate, interval=interval).round(decimals=3)
    
    # Check the company has data downloaded
    if not df.empty:
        outcome = backtest(df)
        outcome_row = [ticker, outcome[0], outcome[1], outcome[2]]

        # Add results for ticker to the larger dataframe
        df_outcome.loc[len(df_outcome)] = outcome_row
    else:
        pass
 
# Print the resulting datafram
print(df_outcome)
