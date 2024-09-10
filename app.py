import os
import pandas as pd
from stocks import Stock
import secFilingAPI
import requests

# Clear previous temp files
for file in ['data.json', '10KQ.txt']:
    try:
        os.remove(f'temp/{file}')
    except FileNotFoundError:
        pass



dl = secFilingAPI.Downloader(user_agent=os.environ.get('sec-user-agent'), cik_map_path='temp/ticker_cik_map.csv', update_cik_map=False)

ticker_symbol = input("Enter ticker symbol [exit with 'exit()']: ")

data = dl.get_data_ticker(ticker_symbol)
details_10KQ = dl.latest_10KQ_details(data)

print(details_10KQ)

response = requests.get(f'https://www.sec.gov/Archives/edgar/data/{details_10KQ["cik"]}/{details_10KQ["accession_num"]}.txt', headers=dl.request_headers)

with open('temp/10KQ.txt', 'w') as f:
    f.write(response.text())