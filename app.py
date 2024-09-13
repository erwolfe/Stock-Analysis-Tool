import os
import json
import sec_API as sec

#Create edgar downloader
edgar = sec.Edgar(user_agent=os.environ.get('sec-user-agent'))

ticker = input("Enter ticker symbol: ")

comp = edgar.get_compnay_by_ticker(ticker)

filings_df = comp.filings

filings_df.to_csv(f'temp/{comp.ticker}_filings.csv')