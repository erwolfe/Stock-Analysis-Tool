import pandas as pd
from financialModelingPrep import api
import requests
import os

def load_statement(fmp:api, symbol:str, statement_type:str, period:str) -> pd.DataFrame:
    try:
        statement = pd.read_csv(f"{symbol}_{statement_type}_{period}.csv")
        print("loaded cached csv")
    except:
        statement = fmp.getStatement(symbol, statement_type, period)
        print("Requested new data from API")
        
        #Clean unwanted rows
        if statement_type == "income-statement":
            statement = statement.drop(["symbol", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "calendarYear","period","link","finalLink"])
        elif statement_type == "balance-sheet-statement":
            statement = statement.drop(["symbol", "reportedCurrency", "cik", "fillingDate", "acceptedDate", "calendarYear","period","link","finalLink"])
        elif statement_type == "cash-flow-statement":
            pass

        statement.to_csv(f"{symbol}_{statement_type}_{period}.csv")

    return statement

fmp = api(os.environ.get("financialModelingPrep_API_Key"))

statement = load_statement(fmp, input("Symbol to get: ").upper(), input("Statement type to get (cash-flow-statement, income-statement, balance-sheet-statement): "), input("Period (type \"annual\"): "))

print(statement.head(5))

