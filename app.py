import os
import sec_API as sec

# Clear previous temp files
for file in ['submissions.json', 'FilingSummary.txt']:
    try:
        os.remove(f'temp/{file}')
    except FileNotFoundError:
        pass


edgar = sec.Edgar(user_agent=os.environ.get('sec-user-agent'))

ticker = input("Enter ticker symbol [exit with 'exit()']: ")

filings = sec.filter_filings_by_form(edgar.get_ticker_filings(ticker), ['10-K'])

filing = filings[0]
print(filing.details['archives_url'])

edgar.get_filing_reports(filing)
print

balance_sheet = edgar.get_statement(filing, 'balance_sheet')


#print(reports)
#edgar.get_statement_location(ticker_symbol, latest_filing.at[0, 'accessionNumber'])