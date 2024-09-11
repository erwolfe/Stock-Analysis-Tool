import os
import requests
import pandas as pd
import json

class Edgar:

    def __init__(self, user_agent:str, cik_map_path:str, update_cik_map:bool = True) -> None:
        self.request_headers = {'User-Agent': user_agent}
        self.base_url = 'https://data.sec.gov/'
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
        if not os.path.exists('temp/'):
            os.mkdir('temp/')
        cik_df.to_csv('temp/ticker_cik_map.csv')

        return cik_df

    def load_cik_map(self) -> pd.DataFrame:
        # Loads the locally stored ticker -> CIK map from a .csv file

        # DataFrame setup
        cik_df = pd.read_csv('temp/ticker_cik_map.csv')
        cik_df.set_index('ticker', inplace=True)

        # Add leading zeros to 'cik_str' (10 digits to comply with sec API requirements)
        cik_df['cik_str'] = cik_df['cik_str'].astype(str).str.zfill(10)

        return cik_df

    def get_cik(self, ticker:str) -> str:
        
        cik = str(self.cik_map.loc[ticker.upper(), 'cik_str']).zfill(10)
        
        return cik

    def get_ticker_submissions(self, ticker:str, filings_only:bool = False) -> (pd.DataFrame | dict):
        cik = self.get_cik(ticker)
        endpoint = f'{self.base_url}submissions/CIK{cik}.json'
        response_json = requests.get(
            endpoint,
            headers=self.request_headers
        ).json()

        with open('temp/data.json', 'w') as f:
            f.write(json.dumps(response_json, indent=4))

        if filings_only:
            df = pd.DataFrame(response_json['filings']['recent'])
            df['accessionNumber'] = df['accessionNumber'].apply(lambda acc: acc.replace('-', ''))
            return df
        return response_json

    def filter_filings_by_form(self, filings:pd.DataFrame, include_forms:list, number_of_filings:int = 0) -> pd.DataFrame:
        df = filings[filings['form'].isin(include_forms)]

        if not number_of_filings == 0:
            df = df.head(number_of_filings)
            
        df.reset_index(inplace=True, drop=True)
        return df

