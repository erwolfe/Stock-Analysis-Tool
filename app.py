import os
import json
import sec_API as sec

#Create edgar downloader
edgar = sec.Edgar(user_agent=os.environ.get('sec-user-agent'))

ticker = input("Enter ticker symbol: ")

comp = edgar.get_compnay_by_ticker(ticker)

gaap = comp.us_gaap

accts_payable = gaap.loc['AccountsPayableCurrent', 'units']
net_income = gaap.loc['NetIncomeLoss', 'units']

open('temp/accounts_payable.json', 'w').write(json.dumps(accts_payable['USD'], indent=2))