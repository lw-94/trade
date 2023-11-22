import pandas as pd
from Klines import Klines
from BackTestEngine import BackTestEngine

c_kline = Klines()

# pairs = c_kline.get_pairs()
# for pair in pairs:

res_df = pd.DataFrame()
print(res_df)

tp_ratio = 1.01


def run(symbol="BTCUSDT"):
    kline_data = c_kline.get_db_data(symbol=symbol)

    bt_engine = BackTestEngine()
    bt_engine.load_data(kline_data)

    # 计算指标，添加
    ma144 = kline_data["close"].rolling(window=144).mean()
    ma169 = kline_data["close"].rolling(window=169).mean()
    kline_data["ma144"] = ma144
    kline_data["ma169"] = ma169
    kline_data["pre_price"] = kline_data["close"].shift(1)

    # 策略
    tp_price = 0
    for i, row in kline_data.iterrows():
        if i < 169 - 1:
            continue
        datetime = row["timestamp"]
        price = float(row["close"])
        pre_price = float(row["pre_price"])
        if (
            pre_price < float(row["ma144"])
            and price > float(row["ma144"])
            and bt_engine.positions == 0
        ):
            tp_price = price * tp_ratio
            vol = 1
            action = "buy"
            bt_engine.execute_order(symbol, datetime, vol, price)
        elif (
            (pre_price < tp_price and price >= tp_price)
            or (pre_price >= float(row["ma144"]) and price < float(row["ma144"]))
        ) and bt_engine.positions > 0:
            vol = -1
            action = "sell"
            bt_engine.execute_order(symbol, datetime, vol, price)

    # bt_engine.create_trade_data_json()
    bt_engine.trades_df.to_csv("docs/trade_data.csv")
    bt_engine.create_bar_chart()


run(symbol="AGIXUSDT")
