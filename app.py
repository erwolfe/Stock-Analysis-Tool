import os
import pandas as pd
from stocks import Stock
import sec_API
import requests
from bs4 import BeautifulSoup

# Clear previous temp files
for file in ['data.json', '10KQ.txt']:
    try:
        os.remove(f'temp/{file}')
    except FileNotFoundError:
        pass

sec = sec_API.Edgar(user_agent=os.environ.get('sec-user-agent'), cik_map_path='temp/ticker_cik_map.csv', update_cik_map=False)

ticker_symbol = input("Enter ticker symbol [exit with 'exit()']: ")

filings_df = sec.get_ticker_submissions(ticker_symbol, filings_only=True)
filings_df = sec.filter_filings_by_form(filings_df, ['10-K'], number_of_filings=1)

endpoint = f'https://www.sec.gov/Archives/edgar/data/{sec.get_cik(ticker_symbol)}/{filings_df.at[0, "accessionNumber"]}.txt'

open('temp/edgar_endpoint.txt', 'w').write(endpoint)

response = requests.get(endpoint, headers=sec.request_headers)

with open('temp/10kq.txt', 'w') as f:
    f.write(response.text)

# Scraping financial statemnts from SEC EDGAR with Python
# https://www.youtube.com/watch?v=gpvG9vYBzwc
