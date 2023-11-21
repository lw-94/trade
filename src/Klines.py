import sqlite3
import datetime
import pandas as pd
import requests
from retrying import retry
import os


class Klines:
    def __init__(self, symbol="BTC"):
        self.table_name = "klines"
        self.symbol = symbol + "USDT"
        # 币安API的基本URL
        self.base_url = "https://fapi.binance.com"
        # open db
        absolute_path = os.path.abspath("db/bn.db")
        print(absolute_path)
        self.conn = sqlite3.connect(absolute_path)
        self.cur = self.conn.cursor()
        print("数据库打开成功")

    # 发送请求以获取所有交易对
    @retry
    def get_pairs(self):
        session = requests.Session()
        response = session.get(f"{self.base_url}/fapi/v1/exchangeInfo")
        if response.status_code == 200:
            exchange_info = response.json()

            # 遍历所有交易对，并筛选出USDT作为计价货币的永续合约
            usdt_perpetual_pairs = [
                pair["symbol"]
                for pair in exchange_info["symbols"]
                if pair["quoteAsset"] == "USDT" and pair["contractType"] == "PERPETUAL"
            ]
        else:
            print(f"请求失败，状态码：{response.status_code}")
        return usdt_perpetual_pairs

    # 获取k线数据
    def get_kline(
        self,
        start_time,
        end_time=int(datetime.datetime.now().timestamp() * 1000),
        interval="1m",
    ):
        """
        # 设置时间间隔（1分钟K线）
        interval = '1m'

        # 获取当前时间和30天前的时间
        end_time = int(datetime.datetime.now().timestamp() * 1000)
        start_time = end_time - (30* 24 * 60 * 60 * 1000)  # 30天前的时间
        """

        session = requests.Session()
        # 存储K线数据的列表
        kline_data_list = []

        params = {
            "symbol": self.symbol,
            "interval": interval,
            "startTime": start_time,
            "end_time": end_time,
            "limit": 1500,  # 最大限制
        }

        response = session.get(f"{self.base_url}/fapi/v1/klines", params=params)
        if response.status_code == 200:
            kline_data_list = response.json()
        else:
            print(f"获取K线数据失败，状态码：{response.status_code}")

        # 将K线数据转换为DataFrame
        kline_df = pd.DataFrame(
            kline_data_list,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )
        kline_df["timestamp"] = pd.to_datetime(kline_df["timestamp"], unit="ms")
        kline_df["timestamp"] = kline_df["timestamp"].astype(str)
        kline_df["symbol"] = self.symbol
        kline_df["timestamp_symbol"] = kline_df["timestamp"] + self.symbol
        return kline_df

    # 标记k线交易数据导入数据库
    def get_data_and_save_to_db(self, start_time, interval="1m"):
        """
        # 开始时间
        start_time

        """
        print(
            "拿1500条(一天1440条), 开始时间：",
            datetime.datetime.fromtimestamp(start_time / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        _data = self.get_kline(start_time=start_time, interval=interval)
        _data["symbol"] = self.symbol
        _data["timestamp_symbol"] = _data["timestamp"] + _data["symbol"]
        cols = (
            "timestamp_symbol",
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        )
        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_symbol TEXT,
            timestamp INTEGER,
            symbol TEXT,
            open TEXT,
            high TEXT,
            low TEXT,
            close TEXT,
            volume TEXT,
            close_time INTEGER,
            quote_asset_volume TEXT,
            number_of_trades INTEGER,
            taker_buy_base_asset_volume TEXT,
            taker_buy_quote_asset_volume TEXT,
            ignore TEXT)
            """
        )
        self.conn.commit()
        for x in _data.index:
            data_list = str(tuple([_data.loc[x, _col] for _col in cols]))
            self.cur.execute(
                f"INSERT OR IGNORE INTO {self.table_name} {str(cols)} VALUES {data_list}"
            )
        self.conn.commit()

    # 获取数据库k线数据
    def get_db_data(self):
        _kline_data = pd.read_sql_query(f"SELECT * FROM {self.table_name}", self.conn)
        return _kline_data
