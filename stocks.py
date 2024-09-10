import pandas as pd
class Stock:
    def __init__(self, ticker_symbol):
        self.symbol = ticker_symbol
        self.financial_data = pd.DataFrame()
        self._return_on_equity = None
        self._return_on_assets = None
        self._net_margin = None

    def return_on_equity(self, year:int = 0) -> float:
        """
        Calculate and return ROE

        :param int year: The year previous to calculate for, relative to current year. For most recent ROE, use year=0. For last year's ROE, use year=1
        """
        if self._return_on_equity == None:
            column = self.financial_data.columns[year]
            try:
                self._return_on_equity = (int(self.financial_data.at["netincomeloss", column]) / int(self.financial_data.at["stockholdersequity", column])) * 100
                return self._return_on_equity
            except:
                print(f"ROE could not be calculated for {self.symbol}")
                return None
        else:
            return self._return_on_equity
        
    def return_on_assets(self, year:int = 0) -> float:
        """
        Calculate and return ROA

        :param int year: The year previous to calculate for, relative to current year. For most recent ROA, use year=0. For last year's ROA, use year=1
        """
        if self._return_on_assets == None:
            column = self.financial_data.columns[year]
            previous_period_column = self.financial_data.columns[year + 1]
            try:
                average_assets = (int(self.financial_data.at["assets", column]) + int(self.financial_data.at["assets", previous_period_column])) / 2
                self._return_on_assets = (int(self.financial_data.at["netincomeloss", column]) / average_assets) * 100
                return self._return_on_assets
            except:
                print(f"ROA could not be calculated for {self.symbol}")
                return None
        else:
            return self._return_on_assets
        
    
if __name__ == "__main__":
    df = pd.read_csv("NEE_financial-data_annual.csv")
    df.set_index("Unnamed: 0", inplace=True)
    
    #df.set_index("Unnamed: 0", inplace=True)
    print(df.head(5))