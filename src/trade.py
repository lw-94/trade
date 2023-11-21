import pandas as pd

from Klines import Klines
from BackTestEngine import BackTestEngine

c_kline = Klines()

kline_data = c_kline.get_db_data()

bt_engine = BackTestEngine()
bt_engine.load_data(kline_data)

# 计算指标，添加
ma20 = kline_data["close"].rolling(window=20).mean()
ma10 = kline_data["close"].rolling(window=10).mean()
kline_data["ma10"] = ma10
kline_data["ma20"] = ma20

# 策略
for i, row in kline_data.iterrows():
    if i <= 18:
        continue
    datetime = row["timestamp"]
    price = row["close"]
    if float(row["ma10"]) > float(row["ma20"]) and bt_engine.positions == 0:
        vol = 1
        action = "buy"
        bt_engine.execute_order(datetime, float(vol), float(price))
        # print(f"Datetime: {datetime}, Action: {action}, Volume: {vol}, Price: {price}")
    elif float(row["ma10"]) < float(row["ma20"]) and bt_engine.positions == 1:
        vol = -1
        action = "sell"
        bt_engine.execute_order(datetime, float(vol), float(price))
        # print(f"Datetime: {datetime}, Action: {action}, Volume: {vol}, Price: {price}")

#
# bt_engine.create_trade_data_json()
# bt_engine.trades_df.to_csv("./trade_data.csv")
bt_engine.create_bar_chart()
