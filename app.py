import os
import finance_tools
import pandas as pd
from sec_API import *

edgar = Edgar(os.environ.get('sec-user-agent'))

ticker = input("Enter the ticker you want: ")
company = edgar.get_compnay_by_ticker(ticker)

roe = finance_tools.return_on_equity(company, 0)

print(f'{roe}')
