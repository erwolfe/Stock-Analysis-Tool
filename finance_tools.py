from edgar import *

def return_on_equity(company:EntityData, year:str):
    financials = company.financials
    income_statement = financials.get_income_statement().to_dataframe()
    balance_sheet = financials.get_balance_sheet().to_dataframe()
    
    net_income = int(income_statement.loc['Net income', year])
    shareholders_equity = int(balance_sheet.loc['Total stockholders’ equity', year])

    return_on_equity = round(net_income / shareholders_equity, 5)
    return return_on_equity