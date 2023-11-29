import datetime
import sys
from Klines import Klines

kl = Klines()

now = int(datetime.datetime.now().timestamp() * 1000)
start_time = now - 24 * 60 * 60 * 1000 * 3

if len(sys.argv) > 1:
    pair = sys.argv[1] + "USDT"
    kl.get_funding_rate_and_save_to_db(symbol=pair, start_time=start_time)
else:
    pairs = kl.get_pairs()
    for pair in pairs:
        kl.get_funding_rate_and_save_to_db(symbol=pair, start_time=start_time)
