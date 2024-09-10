import requests
import pandas as pd
import json

class Downloader:

    def __init__(self, user_agent:str, cik_map_path:str, update_cik_map:bool = True) -> None:
        self.request_headers = {'User-Agent': user_agent}
        self.base_url = 'https://data.sec.gov/submissions/'
        self.cik_map = None

        if update_cik_map:
            self.cik_map = self.update_cik_map(self.request_headers)
        else:
            try:
                self.cik_map = self.load_cik_map()
            except:
                self.cik_map = self.update_cik_map(self.request_headers)

    def update_cik_map(self, headers:dict) -> pd.DataFrame:
        # Updates local .csv copy of ticker -> CIK mapping from SEC and returns dataframe of updated map
        
        tickers = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=headers
        )

        # DataFrame setup
        cik_df = pd.DataFrame.from_dict(tickers.json())
        cik_df = cik_df.T
        cik_df.set_index('ticker', inplace=True)

        # Add leading zeros to 'cik_str' (10 digits to comply with sec API requirements)
        cik_df['cik_str'] = cik_df['cik_str'].astype(str).str.zfill(10)

        # Save new map to local .csv
        cik_df.to_csv('ticker_cik_map.csv')

        return cik_df

    def load_cik_map(self) -> pd.DataFrame:
        # Loads the locally stored ticker -> CIK map from a .csv file

        # DataFrame setup
        cik_df = pd.read_csv('ticker_cik_map.csv')
        cik_df.set_index('ticker', inplace=True)

        # Add leading zeros to 'cik_str' (10 digits to comply with sec API requirements)
        cik_df['cik_str'] = cik_df['cik_str'].astype(str).str.zfill(10)

        return cik_df

    def get_cik(self, ticker:str) -> str:
        return self.cik_map.loc[ticker.upper(), 'cik_str']

    def get_data(self, cik:str):
        endpoint = f'{self.base_url}CIK{cik}.json'
        response = requests.get(
            endpoint,
            headers=self.request_headers
        )

        return response.json()

    def get_data_ticker(self, ticker:str) -> json:
        cik = self.get_cik(ticker)
        data = self.get_data(cik)

        return data


dl = Downloader(user_agent="erwolfe40@gmail.com", cik_map_path='ticker_cik_map.csv', update_cik_map=False)

ticker_symbol = input("Enter ticker symbol [exit with 'exit()']: ")
"""
while str(ticker_symbol).lower() != "exit()":
    
    try:
        cik = dl.get_cik(ticker_symbol)
        print(cik)
    except KeyError:
        print('Ticker or command not found')
    
    ticker_symbol = input("Enter ticker symbol [exit with 'exit()']: ")
"""

data = dl.get_data_ticker(ticker_symbol)

recent_filings = data['filings']['recent']

accession_numbers = recent_filings['accessionNumber']
forms = recent_filings['form']
report_dates = recent_filings['reportDate']

recent10qs = [{'form': form, 'date': date, 'accession_num': accession} for date, accession, form in zip(report_dates, accession_numbers, forms) if form == "10-Q" or form == "10-K"][:4]

latest_accession = recent10qs[0]['accession_num']
cik = dl.get_cik(ticker_symbol)
response = requests.get(f'https://www.sec.gov/Archives/edgar/data/{cik}/{latest_accession}.txt', headers=dl.request_headers)
print(latest_accession, cik)

