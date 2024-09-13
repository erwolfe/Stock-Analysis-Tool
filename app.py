import os
import finance_tools
from edgar import *

set_identity(os.environ.get('sec-user-agent'))

company = Company("AMD")

roe = f'{finance_tools.return_on_equity(company, "2023") * 100:.2f}%'

print(roe)