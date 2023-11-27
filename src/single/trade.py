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
    # kline_data.to_csv(f"{symbol}-klines.csv")
    bt_engine = BackTestEngine()
    bt_engine.load_data(kline_data)
    # 执行策略
    bt_engine.s_sma169(symbol=symbol)
    #
    # bt_engine.create_trade_data_json()
    bt_engine.trades_df.to_csv("docs/trade_data.csv")
    bt_engine.create_trade_data_json()
    bt_engine.create_bar_chart()


run(symbol="BTCUSDT")
