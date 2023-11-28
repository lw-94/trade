from Klines import Klines
import datetime

kl = Klines()

pairs = kl.get_pairs()

now = int(datetime.datetime.now().timestamp() * 1000)
start_time = now - 24 * 60 * 60 * 1000 * 1

# only BTC
kl.get_data_and_save_to_db(start_time=start_time, symbol="BTCUSDT")

# all
# for pair in pairs:
#     kl.get_data_and_save_to_db(start_time=start_time, symbol=pair)

print("done")
