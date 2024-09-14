import os
import finance_tools
import pandas as pd
from sec_API import *
import json

edgar = Edgar(os.environ.get('sec-user-agent'))

ticker = input("Enter the ticker you want: ")
company = edgar.get_compnay_by_ticker(ticker)

filings = company.filings
print(filings.head(35))

#open(f'temp/{company.ticker}_filings.json', 'w').write(json.dumps(submissions, indent=2))