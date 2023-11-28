import sys
from Klines import Klines
import datetime

kl = Klines()

pairs = kl.get_pairs()

# TODO: 拿多久时间的数据改成参数，现在固定为1天
now = int(datetime.datetime.now().timestamp() * 1000)
start_time = now - 24 * 60 * 60 * 1000 * 1

if len(sys.argv) > 1:
    # single
    pair = sys.argv[1] + "USDT"
    kl.get_data_and_save_to_db(start_time=start_time, symbol=pair)
else:
    # all
    for pair in pairs:
        kl.get_data_and_save_to_db(start_time=start_time, symbol=pair)

print("done")
