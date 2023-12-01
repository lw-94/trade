from Klines import Klines

from finta import TA

ck = Klines()

df = ck.get_db_data(pair="BTCUSDT")


# print(TA.EMA(df, 144))
