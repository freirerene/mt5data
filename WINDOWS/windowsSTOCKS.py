import argparse
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("codigo")
parser.add_argument("-d", "--day")

args = parser.parse_args()
codigo = args.codigo
day = args.day

path = "Z:\\home\\rene\\.mt5\\drive_c\\Program Files\\MetaTrader 5\\terminal64.exe"
mt5.initialize(path)

day_dt = f"{day} 18:00:00"
day_dt = datetime.fromisoformat(day_dt)

x = mt5.copy_rates_from(codigo, mt5.TIMEFRAME_H1, day_dt, 100)
x = pd.DataFrame(x)

x['time'] = pd.to_datetime(x['time'], unit='s')
df_data = x.copy()

df_data = df_data.drop_duplicates()
df_data = df_data.sort_values(by='time')
df_data['codigo'] = codigo

df_data.to_csv(f"data/{codigo}/{day}.csv", index=False)