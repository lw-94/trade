import sys
from Klines import Klines
from BackTestEngine import BackTestEngine

c_kline = Klines()


def trade(pair="BTCUSDT", interval=""):
    kline_data = c_kline.get_db_data(pair=pair, interval=interval)
    # 源数据
    # kline_data.to_csv(f"{pair}-klines.csv")
    bt_engine = BackTestEngine()
    bt_engine.load_data(kline_data)
    # 执行策略
    # TODO：策略也可加入命令行参数
    bt_engine.s_sma169(pair=pair)
    # 产出
    bt_engine.create_trade_data_json(
        pair=pair, file_path=f"docs/trade_data_{pair}.json"
    )
    bt_engine.trades_df.to_csv(f"docs/trade_data_{pair}.csv")
    bt_engine.create_bar_chart()


if len(sys.argv) > 1:
    pair = sys.argv[1] + "USDT"
    interval = ""
    if len(sys.argv) > 2:
        interval = sys.argv[2]
    trade(pair=pair, interval=interval)
else:
    trade()
