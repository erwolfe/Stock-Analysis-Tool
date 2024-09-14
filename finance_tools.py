import pandas as pd
from sec_API import Company

def return_on_equity(company:Company, periods_ago:int):
    financials = company.financials
    column = financials.columns[periods_ago]

    net_income_dict = financials.loc['Net Income (Loss) Attributable to Parent', column]
    if not pd.isna(net_income_dict):
        net_income = net_income_dict.get('value')
    else:
        net_income = None
        print(f'Data not available for selected period: Net income {periods_ago} period(s) ago')

    shareholders_equity_dict = financials.loc["Stockholders' Equity Attributable to Parent", column]
    if not pd.isna(shareholders_equity_dict):
        shareholders_equity = shareholders_equity_dict.get('value')
    else:
        shareholders_equity = None
        print(f"Data not available for selected period: Shareholders' Equity {periods_ago} period(s) ago")

    return_on_equity = round(net_income / shareholders_equity, 5)
    return return_on_equity
