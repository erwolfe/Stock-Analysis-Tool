import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Union, List

class Edgar:
    """Handles downloading data from SEC endpoints
    """
    def __init__(self, user_agent:str) -> None:
        """Initializes an instance of the Edgar class

        Args:
            user_agent (str): SEC-required user agent. Format: "John Smith address@domain.com"
        """
        self.request_headers = {'User-Agent': user_agent}
        self.base_url = 'https://data.sec.gov/'
        self.cik_map = self.get_cik_map()

    def get_cik_map(self) -> pd.DataFrame:
        """Requests JSON file that maps company tickers, names and CIKs. Saves a local JSON copy and returns a DataFrame.

        Returns:
            pd.DataFrame: Ticker-indexed DataFrame with columns for CIK and company name
        """
        map = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers=self.request_headers
        ).json()

        open('temp/tickers.json', 'w').write(json.dumps(map, indent=4))

        # DataFrame setup
        df = pd.DataFrame.from_dict(map).transpose().set_index('ticker')

        return df

    def get_company_by_ticker(self, ticker:str) -> Union['Company', None]:
        """Generates a Company object from a provided ticker symbol

        Args:
            ticker (str): Ticker symbol of the company to be initialized e.g. AAPL

        Returns:
            Union['Company', None]: An instance of the sec_API.Company class. None if a matching ticker is not found
        """
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
        
    def _get_company_facts(self, company:'Company') -> dict:
        """Retrieves facts for a company from the SEC's facts endpoint

        Args:
            company (Company): sec_API.Company object of which to fetch facts for

        Returns:
            dict: A dictionary representation of the JSON response from the facts endpoint
        """
        cik = company.cik
        url_extension = 'api/xbrl/companyfacts/CIK'
        endpoint = f'{self.base_url}{url_extension}{cik}.json'

        response = requests.get(
            endpoint,
            headers=self.request_headers
        ).json()

        return response
    
    def _get_company_submissions(self, company:'Company') -> dict:
        """Retrieves submissions for a company from the SEC's submissions endpoint

        Args:
            company (Company): sec_API.Company object of which to fetch submissions for

        Returns:
            dict: A dictionary representation of the JSON response from the submissions endpoint
        """
        cik = company.cik
        url_extension = 'submissions/CIK'
        endpoint = f'{self.base_url}{url_extension}{cik}.json'

        response = requests.get(
            endpoint,
            headers=self.request_headers
        ).json()
        
        return response
    
class Company:
    def __init__(self, edgar:'Edgar', ticker=None, cik=None, name=None) -> None:
        """Initializes an instance of the Company class. Not recommended to be called directly. Instead, use Edgar.get_company_by_ticker() to create a Company obejct.

        Args:
            edgar (Edgar): The Edgar object which will facilitate any interaction with the SEC's API
            ticker (_type_, optional): Ticker symbol of the Company, e.g. AAPL. Defaults to None.
            cik (_type_, optional): The Company's Central Index Key (CIK), e.g. 0000320193. Defaults to None.
            name (_type_, optional): The Company's long name, e.g. Apple Inc.. Defaults to None.
        """
        self.ticker = ticker
        self.cik = cik
        self.name = name
        self.edgar=edgar
        self._facts = None
        self._us_gaap = None
        self._financials = None
        self._filings = None

    @property
    def facts(self) -> dict:
        """Facts for the company from the SEC's facts endpoint. Fetched through Edgar object

        Returns:
            dict: A dictionary representation of facts endpoint's JSON response
        """
        if self._facts is None:
            self._facts = self.edgar._get_company_facts(self)
        return self._facts
    
    @property
    def us_gaap(self) -> dict:
        """US GAAP line-items found in the company's facts

        Returns:
            dict: Extracted GAAP line-items in a messy, nested format. Reccommended to use Company.financials instead
        """
        if self._us_gaap is None:
            us_gaap_json = self.facts['facts']['us-gaap']
            self._us_gaap = us_gaap_json
        return self._us_gaap
        
    @property
    def financials(self) -> pd.DataFrame:
        """Formatted US GAAP financial information

        Returns:
            pd.DataFrame: Label indexed DataFrame with columns for each period with available data
        """
        if self._financials is None:
            financials = {}
            for value in self.us_gaap.values():
                key = value['label']
                unit = list(value['units'].keys())[0]

                for file in value['units'][unit]:
                    name = f"{file.get('form')}_{file.get('fp')}_{file.get('fy')}"
                    financials.setdefault(name, {})[key] = {
                        'value': file.get('val'), 
                        'unit': unit
                    }

            df = pd.DataFrame(financials)
            df_reversed_cols = df[df.columns[::-1]]

            self._financials = df_reversed_cols
        return self._financials
    
    def filings(
            self,
            form_type:Union[str, List[str]] = None,
            report_date_start:datetime = None,
            report_date_end:datetime = None,
            filing_date_start:datetime = None,
            filing_date_end:datetime = None,
            is_xbrl:bool = None,
    ) -> 'FilingsList':
        """Extract and filter specific forms from the Company's filings, based on several criteria. Omitting an arg applies no filters to that field.

        Args:
            form_type (Union[str, List[str]], optional): Type of forms to include e.g. '10-K'. Defaults to None.
            report_date_start (datetime, optional): Earliest report_date date to include. Defaults to None.
            report_date_end (datetime, optional): Latest report_date date to include. Defaults to None.
            filing_date_start (datetime, optional): Earliest filing_date date to include. Defaults to None.
            filing_date_end (datetime, optional): Latest filing_date date to include. Defaults to None.
            is_xbrl (bool, optional): Include only filings that are XBRL formatted? Defaults to None.

        Returns:
            FilingsList: List containing only Filings objects that match all filter criteria
        """
        # Get filings for the Company if they havent already been fetched.
        if self._filings is None:
            submissions = self.edgar._get_company_submissions(self)

            rfs = submissions['filings']['recent']

            z = zip(
                rfs['accessionNumber'],
                rfs['filingDate'],
                rfs['reportDate'],
                rfs['form'],
                rfs['items'],
                rfs['isXBRL'],
                rfs['primaryDocument']
            )

            self._filings = FilingsList([
                Filing(
                    company=self,
                    accession=accn,
                    filing_date=filing_date,
                    report_date=report_date,
                    form=form,
                    items=items,
                    is_xbrl=is_xbrl,
                    primary_document=primary_doc
                )
                for accn, filing_date, report_date, form, items, is_xbrl, primary_doc in z
            ])

        filings = self._filings.to_pandas()

        # Filter the filings according to criteria
        if form_type is not None:
            if isinstance(form_type, str):
                form_type = [form_type]
            filings = filings[filings['form'].isin(form_type)]

        if report_date_start is not None:
            filings = filings[filings['report_date'] >= report_date_start]

        if report_date_end is not None:
            filings = filings[filings['report_date'] <= report_date_end]

        if filing_date_start is not None:
            filings = filings[filings['filing_date'] >= filing_date_start]

        if filing_date_end is not None:
            filings = filings[filings['filing_date'] <= filing_date_end]

        if is_xbrl is not None:
            filings = filings[filings['is_xbrl'] == is_xbrl]

        filing_map = {filing.accession: filing for filing in self._filings}

        filings = FilingsList([filing_map[accession] for accession in filings['accession']])

        return filings

class FilingsList(list['Filing']):
    """Inherits from python list to add pandas DataFrame conversion functionality

    Args:
        list (Filing): _description_
    """
    def to_pandas(self) -> pd.DataFrame:
        """Converts a FilingsList object to a DataFrame representation of the data

        Returns:
            pd.DataFrame: List of filings formatted as a DataFrame
        """
        df = pd.DataFrame([filing.__dict__ for filing in self])

        df['filing_date'] = pd.to_datetime(df['filing_date'])
        df['report_date'] = pd.to_datetime(df['report_date'])

        df.drop(columns=['company', '_reports'], inplace=True)

        return df

class Filing:
    """Represents a single filing submitted by a company to the SEC, instance variable accession used as unique identifier
    """
    def __init__(self, company:Company = None, accession:str = None, filing_date:str = None, report_date:str = None, form:str = None, items:str = None, is_xbrl:str = None, primary_document:str = None) -> None:
        """Initializes an instance fo the Filing class. Reccommended to not call directly, use Company.get_filings() to get a Company's Filings

        Args:
            accession (str, optional): Defaults to None.
            filing_date (str, optional): Defaults to None.
            report_date (str, optional): Defaults to None.
            form (str, optional): Defaults to None.
            items (str, optional): Defaults to None.
            is_xbrl (str, optional): Defaults to None.
            primary_document (str, optional): Defaults to None.
        """
        self.company = company
        self.accession = accession
        self.filing_date = filing_date
        self.report_date = report_date
        self.form = form
        self.items = items
        self.is_xbrl = is_xbrl
        self.primary_document = primary_document

        self._reports = None

    def reports(self, report_name:Union[str, List[str]] = None) -> 'ReportsList':
        if self._reports is None:
            base_url = 'https://sec.gov/Archives/edgar/data/'
            cik = self.company.cik
            accession = str(self.accession).replace('-', '')
            endpoint = f'{base_url}{cik}/{accession}/FilingSummary.xml'

            filing_summary = requests.get(
                endpoint,
                headers = self.company.edgar.request_headers
            ).content.decode('utf-8')

            filing_summary = BeautifulSoup(filing_summary, 'lxml-xml')

            reports = filing_summary.findAll('Report')

            self._reports = ReportsList([
                Report(
                    html_filename=report.find('HtmlFileName').get_text(strip=True) if report.find('HtmlFileName') else None,
                    long_name=report.find('LongName').get_text(strip=True) if report.find('LongName') else None,
                    report_type=report.find('ReportType').get_text(strip=True) if report.find('ReportType') else None,
                    short_name=report.find('ShortName').get_text(strip=True) if report.find('ShortName') else None,
                    position=report.find('Position').get_text(strip=True) if report.find('Position') else None
                )
                for report in reports
            ])
        
        if report_name is not None:
            reports = ReportsList([
                report for report in self._reports if report.short_name in report_name
            ])
        else:
            return self._reports

        return reports

class ReportsList(list['Report']):
    def to_pandas(self):
        df = pd.DataFrame([report.__dict__ for report in self])
        df.set_index('short_name', inplace=True)
        return df
    
class Report:
    def __init__(self, html_filename:str = None, long_name:str = None, report_type:str = None, short_name:str = None, position = None) -> None:
        self.html_filename = html_filename
        self.long_name = long_name
        self.report_type = report_type
        self.short_name = short_name
        try:
            self.position = int(position)
        except:
            self.position = position