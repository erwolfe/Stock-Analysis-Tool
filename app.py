import os
import finance_tools
import pandas as pd
from sec_API import *
from datetime import datetime
import json

edgar = Edgar(os.environ.get('sec-user-agent'))

ticker = input("Enter the ticker you want: ")
company = edgar.get_company_by_ticker(ticker)

latest_tenQ = company.get_filings(form_type='10-Q')[0]

reports = latest_tenQ.get_reports()

print(reports.to_pandas())