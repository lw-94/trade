from Klines import Klines
import datetime

kl = Klines()
now = int(datetime.datetime.now().timestamp() * 1000)
start_time = now - 24 * 60 * 60 * 1000 * 1
kl.get_data_and_save_to_db(start_time=start_time)
