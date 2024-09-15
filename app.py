import os
import finance_tools
import pandas as pd
from sec_API import *
from datetime import datetime
import json

edgar = Edgar(os.environ.get('sec-user-agent'))

ticker = input("Enter the ticker you want: ")
company = edgar.get_company_by_ticker(ticker)

recent_tenQ_df = company.get_filings(form_type='10-Q').to_pandas()

print(recent_tenQ_df)