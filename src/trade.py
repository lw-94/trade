from Klines import Klines
from BackTestEngine import BackTestEngine

c_kline = Klines()


def trade(pair="BTCUSDT"):
    kline_data = c_kline.get_db_data(pair=pair)
    # 源数据
    # kline_data.to_csv(f"{pair}-klines.csv")
    bt_engine = BackTestEngine()
    bt_engine.load_data(kline_data)
    # 执行策略
    bt_engine.s_sma169(pair=pair)
    # 产出
    bt_engine.create_trade_data_json(
        pair=pair, file_name=f"docs/trade_data_{pair}.json"
    )
    bt_engine.trades_df.to_csv(f"docs/trade_data_{pair}.csv")
    bt_engine.create_bar_chart()


trade("BTCUSDT")
