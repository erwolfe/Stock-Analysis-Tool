import json
import requests
import pandas as pd

class Edgar:
    def __init__(self, user_agent:str) -> None:
        self.request_headers = {'User-Agent': user_agent}
        self.base_url = 'https://data.sec.gov/'
        self.cik_map = self.get_cik_map()

    def get_cik_map(self) -> pd.DataFrame:
        map = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=self.request_headers
        ).json()

        open('temp/tickers.json', 'w').write(json.dumps(map, indent=4))

        # DataFrame setup
        df = pd.DataFrame.from_dict(map).transpose().set_index('ticker')

        return df

    def get_compnay_by_ticker(self, ticker:str) -> 'Company':
        ticker = ticker.upper()
        try:
            cik = str(self.cik_map.loc[ticker, 'cik_str']).zfill(10)
            name = str(self.cik_map.loc[ticker, 'title'])

            return Company(
                ticker=ticker,
                cik=cik,
                name=name,
                edgar=self
            )
        except KeyError:
            return None
        
    def _get_company_facts(self, company:'Company'):
        cik = company.cik
        url_extension = 'api/xbrl/companyfacts/CIK'
        endpoint = f'{self.base_url}{url_extension}{cik}.json'

        response = requests.get(
            endpoint,
            headers=self.request_headers
        ).json()

        return response
    
class Company:
    def __init__(self, edgar:'Edgar', ticker=None, cik=None, name=None) -> None:
        self.ticker = ticker
        self.cik = cik
        self.name = name
        self.edgar=edgar
        self._facts = None
        self._us_gaap = None

    @property
    def facts(self):
        # If facts has not been fetched yet, get them via Edgar
        if self._facts is None:
            self._facts = self.edgar._get_company_facts(self)
        return self._facts
    
    @property
    def us_gaap(self) -> pd.DataFrame:
        if self._us_gaap is None:
            us_gaap_json = self.facts['facts']['us-gaap']
            self._us_gaap = us_gaap_json
        return self._us_gaap
        

