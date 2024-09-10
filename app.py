import pandas as pd
from financialModelingPrep import api
from stocks import Stock
import os

if input("Use cached financial data? (y/n): ").upper() == "Y":
    useCached = True
else:
    useCached = False

while True:
    try:
        number_of_stocks = int(input("Enter quantity of stocks to be compared: "))
        if number_of_stocks <= 0:
            print("    <!> Qty of stocks must be > 0")
            continue
        else:
            break
    except:
        print("    <!> Qty of stocks must be an integer value")
        continue

stocks = []
for i in range(number_of_stocks):
    symbol = input(f"Enter stock #{i + 1}'s ticker symbol: ").upper()
    stocks.append(Stock(symbol))

fmp = api(os.environ.get("financialModelingPrep_API_Key"))

for stock in stocks:
    if useCached:
        try:
            stock.financial_data = pd.read_csv(f"{stock.symbol}_financial-data_annual.csv")
            stock.financial_data.set_index("Unnamed: 0", inplace=True)
        except:
            stock.financial_data = fmp.getStatement(stocks[i].symbol, "financial-statement-full-as-reported", "annual")
            pd.DataFrame.to_csv(stocks[i].financial_data, f"{stocks[i].symbol}_financial-data_annual.csv")

    
    
for s in stocks:
    """
    print(s.financial_data.head())
    print(s.financial_data.columns)
    print(s.financial_data.index)
    """
    symbol = s.symbol
    column = s.financial_data.columns[0]
    se = s.financial_data.at["stockholdersequity", column]
    ni = s.financial_data.at["netincomeloss", column]
    roe = s.return_on_equity()
    roa = s.return_on_assets()
    print(f"Symbol: {symbol}\nStockholder's Equity: {se}\nNet Income: {ni}\nROE: {roe}\nROA: {roa}\n")