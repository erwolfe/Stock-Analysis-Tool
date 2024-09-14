import os
import finance_tools
import pandas as pd
from sec_API import *
from datetime import datetime
import json

edgar = Edgar(os.environ.get('sec-user-agent'))

ticker = input("Enter the ticker you want: ")
company = edgar.get_company_by_ticker(ticker)
company.facts
filings = company.get_forms(form_type='10-Q', report_date_end=datetime(2023, 12, 31))

print(company.name)