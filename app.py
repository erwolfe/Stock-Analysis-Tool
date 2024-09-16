import os
import finance_tools
import pandas as pd
from sec_API import *
from datetime import datetime
import json

edgar = Edgar(os.environ.get('sec-user-agent'))

ticker = input("Enter the ticker you want: ")
company = edgar.get_company_by_ticker(ticker)

latest_tenQ = company.filings(form_type='10-Q')[0]

reports_list = ['Condensed Consolidated Statements of Operations']
reports = latest_tenQ.reports(reports_list)

"""
for report in reports:
    report_df = report.get_data()
    report_df.to_csv(f'temp/{company.ticker}_{report.short_name}.csv')"""

income_statement = reports[0]

