import pandas as pd

from GETDATA import get_stocks_history

d_i = '2018-04-10'
d_f = '2024-09-07'

df = pd.read_csv('acoes.csv')

for i, row in df.iterrows():
    codigo = row['codigo']
    print(codigo)
    get_stocks_history(codigo, d_i, d_f)
    print('='*100)
