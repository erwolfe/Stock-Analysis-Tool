import requests
import pandas as pd
import os

class api:
    def __init__(self, apikey:str) -> None:
        self.api_key = apikey
        self.baseurl = "https://financialmodelingprep.com/api/v3/"

    def getStatement(self, symbol:str, report_type:str, period:str) -> pd.DataFrame:
        
        fullurl = f'{self.baseurl}{report_type}/{symbol}?period={period}&apikey={self.api_key}'
        response = requests.get(fullurl)
        df = pd.json_normalize(response.json())
        df.set_index("date", inplace=True)
        df = df.T
        
        return df
    
    def historicalData(self, symbol:str, from_date:str, to_date:str) -> pd.DataFrame:

        fullurl = f'{self.baseurl}historical-price-full/{symbol}?from={from_date}&to={to_date}&apikey={self.api_key}'
        response = requests.get(fullurl)
        df = pd.json_normalize(response.json())

        return df.transpose()
    
    def getQuote(self, symbol:str):
        fullurl = f'{self.baseurl}quote/{symbol}?apikey={self.api_key}'
        response = requests.get(fullurl)
        df = pd.json_normalize(response.json())
        df = df.T

        return df


if __name__ == "__main__":
    fmp = api(os.environ.get("financialModelingPrep_API_Key"))

    symbol = "AMD"

    #df = fmp.getStatement(symbol,  "financial-statement-full-as-reported", "annual")
    df = fmp.getQuote("NVDA")

    print(df.head(5))
