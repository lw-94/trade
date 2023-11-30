from Klines import Klines

ck = Klines()

df = ck.get_db_data(pair="BTCUSDT", interval="5h")

print(df)
