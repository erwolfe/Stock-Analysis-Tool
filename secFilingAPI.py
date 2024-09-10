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
        return self.cik_map.loc[ticker.upper(), 'cik_str']

    def get_data(self, cik:str) -> dict:
        endpoint = f'{self.base_url}CIK{cik}.json'
        response = requests.get(
            endpoint,
            headers=self.request_headers
        )

        json_response = response.json()

        with open('temp/data.json', 'w') as f:
            f.write(json.dumps(json_response, indent=4))

        return json_response

    def get_data_ticker(self, ticker:str) -> dict:
        cik = self.get_cik(ticker)
        data = self.get_data(cik)

        return data

    def latest_10KQ_details(self, data:dict) -> dict:
        # Finds the details (including accession number) of the latest 10-Q or 10-K (whichever is more recent) for the given json data
        # return format: {
        #     'form': form type (10-K or 10-Q)
        #     'date': reporting date for the form
        #     'accession_num': unique accession number for retrieving form from SEC EDGAR database
        # }

        # All 'recent filings' included in the SEC json data
        recent_filings = data['filings']['recent']

        # Values are lists of their respective attribute values
        cik = data['cik']
        accession_numbers = recent_filings['accessionNumber']
        forms = recent_filings['form']
        report_dates = recent_filings['reportDate']

        # Form dictionary of details for latest 10-K or 10-Q
        # Get only values in accession_numbers and report_dates lists where forms list == '10-K' or '10-Q'
        latest_10QK = [{'cik': cik, 'form': form, 'date': date, 'accession_num': accession} for date, accession, form in zip(report_dates, accession_numbers, forms) if form == "10-Q" or form == "10-K"][:1]

        return latest_10QK
