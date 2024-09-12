import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

class Edgar:

    def __init__(self, user_agent:str) -> None:
        self.request_headers = {'User-Agent': user_agent}
        self.base_url = 'https://data.sec.gov/'

    def get_cik(self, ticker:str) -> str:
    
        tickers = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=self.request_headers
        )

        # DataFrame setup
        cik_df = pd.DataFrame.from_dict(tickers.json())
        cik_df = cik_df.T
        cik_df.set_index('ticker', inplace=True)

        # Add leading zeros to 'cik_str' (10 digits to comply with sec API requirements)
        cik = str(cik_df.loc[ticker.upper(), 'cik_str']).zfill(10)
    
        return cik

    def get_filings(self, ticker:str, cik:str, clean_accession:bool = True) -> list['Filing']:
        submissions = self.get_submissions(cik)
        
        df = pd.DataFrame(submissions['filings']['recent'])
        if clean_accession:
            df['accessionNumber'] = df['accessionNumber'].apply(lambda acc: acc.replace('-', ''))
        
        #print(df.head(10))

        filings = []
        for row in df.iterrows():
            f = list(row)[1].to_dict()

            accession = f['accessionNumber']
            form = f['form']
            report_date = f['reportDate']

            filings.append(
                Filing(
                    accession,
                    form,
                    ticker,
                    report_date,
                    cik
                )
            )

        return filings

    def get_ticker_filings(self, ticker:str, clean_accession:bool = True) -> list['Filing']:
        cik = self.get_cik(ticker)
        return self.get_filings(ticker, cik, clean_accession)

    def get_submissions(self, cik:str):
        endpoint = f'{self.base_url}submissions/CIK{cik}.json'
        response_json = requests.get(
            endpoint,
            headers=self.request_headers
        ).json()

        with open('temp/submissions.json', 'w') as f:
            f.write(json.dumps(response_json, indent=4))

        return response_json
    
    def get_ticker_submissions(self, ticker:str):
        # Unused for now, just in case I need to access the JSON submissions by ticker
        cik = self.get_cik(ticker)
        return self.get_submissions(cik)

    def get_statement_address(self, ticker_symbol:str, accession_number:str, statement:str):
        # param statement: 'balance_sheet', 'income_statement', or 'cash_flow_statement'
        
        cik = self.get_cik(ticker_symbol)

        base_url = f'{archives_base_url}{cik}/{accession_number}/'
        response = requests.get(
            f'{base_url}FilingSummary.xml',
            headers=self.request_headers
        ).content.decode('utf-8')

        summary_soup = BeautifulSoup(response, 'lxml-xml')
        reports_soup = summary_soup.findAll('Report')

        acceptable_names = statement_keys_map[statement]

        for report in reports_soup:
            name = report.find('ShortName')
            name_html = report.find('HtmlFileName')

            if name.text and name.text in acceptable_names:
                return f'{base_url}{name_html}'

    def get_filing_reports(self, filing:'Filing'):
        base_url = Filing.base_url
        cik = filing.details['cik']
        accession = str(filing.details['accession'])

        endpoint = f'{base_url}{cik}/{accession}/FilingSummary.xml'
        
        response = requests.get(
            endpoint,
            headers=self.request_headers
        ).content.decode('utf-8')

        open('temp/FilingSummary.xml', 'w').write(response)

        filing_summary_soup = BeautifulSoup(response, 'lxml-xml')
        response_codes = filing_summary_soup.findAll('Code')
        for code in response_codes:
            if code.text and code.text == 'NoSuchKey':
                raise requests.HTTPError(f'No file found at {endpoint}')

        reports = filing_summary_soup.findAll('Report')

        short_names = []
        html_names = []
        for report in reports:
            name = report.find('ShortName')
            html_name = report.find('HtmlFileName')

            if name:
                short_names.append(name.text)
            else:
                short_names.append('')

            if html_name:
                html_names.append(html_name.text)
            else:
                html_names.append('')
                
        z = list(zip(short_names, html_names))
        reports = [{name: file} for name, file in z]
        filing.reports = reports

        return filing.reports

class Filing:
    base_url = 'https://www.sec.gov/Archives/edgar/data/'

    def __init__(self, accession = None, form = None, ticker = None, report_date = None, cik = None):
        self.details = {
            'accession': accession,
            'form': form,
            'ticker': ticker,
            'cik': cik,
            'report_date': report_date
        }

        self.reports = []


class Report:
    def __init__(self, name = None, html_file_name = None):
        self.name = name
        self.html_file_name = html_file_name

        if html_file_name:
            self.data_from_html(html_file_name)
        else:
            self.data = None

    def data_from_html(self, address):

        # set self.data and then return self

        return self

######################
# Standalone Functions
######################
def filter_filings_by_form(filings:list['Filing'], include_forms:list, number_of_filings:int = 0) -> list['Filing']:
    filtered_filings = [filing for filing in filings if filing.details['form'] in include_forms]
    return filtered_filings

######################
# Initialization
######################
archives_base_url = 'https://www.sec.gov/Archives/edgar/data/'

statement_keys_map = {
    "balance_sheet": [
        "balance sheet",
        "balance sheets",
        "statement of financial position",
        "consolidated balance sheets",
        "consolidated balance sheet",
        "consolidated financial position",
        "consolidated balance sheets - southern",
        "consolidated statements of financial position",
        "consolidated statement of financial position",
        "consolidated statements of financial condition",
        "combined and consolidated balance sheet",
        "condensed consolidated balance sheets",
        "consolidated balance sheets, as of december 31",
        "dow consolidated balance sheets",
        "consolidated balance sheets (unaudited)",
    ],
    "income_statement": [
        "income statement",
        "income statements",
        "statement of earnings (loss)",
        "statements of consolidated income",
        "consolidated statements of operations",
        "consolidated statement of operations",
        "consolidated statements of earnings",
        "consolidated statement of earnings",
        "consolidated statements of income",
        "consolidated statement of income",
        "consolidated income statements",
        "consolidated income statement",
        "condensed consolidated statements of earnings",
        "consolidated results of operations",
        "consolidated statements of income (loss)",
        "consolidated statements of income - southern",
        "consolidated statements of operations and comprehensive income",
        "consolidated statements of comprehensive income",
    ],
    "cash_flow_statement": [
        "cash flows statement",
        "cash flows statements",
        "statement of cash flows",
        "statements of consolidated cash flows",
        "consolidated statements of cash flows",
        "consolidated statement of cash flows",
        "consolidated statement of cash flow",
        "consolidated cash flows statements",
        "consolidated cash flow statements",
        "condensed consolidated statements of cash flows",
        "consolidated statements of cash flows (unaudited)",
        "consolidated statements of cash flows - southern",
    ],
}
