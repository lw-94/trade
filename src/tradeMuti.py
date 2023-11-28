from Klines import Klines
from BackTestEngine import BackTestEngine
import utils

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
    return bt_engine.create_trade_data_json(
        pair=pair, file_name=f"docs/trade_data_{pair}.json", create_file=False
    )


content = "{"
pairs = c_kline.get_pairs()[:10]
for idx, pair in enumerate(pairs):
    json = trade(pair)
    content += f'"{pair[:-4]}":{json}'
    if idx != len(pairs) - 1:  # not last pair
        content += ","
content += "}"
utils.write_file("docs/trade_data_muti.json", content)
print(f"{len(pairs)}个币数据")
