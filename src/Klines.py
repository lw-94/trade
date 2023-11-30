import sqlite3
import datetime
import pandas as pd
import requests
from retrying import retry
import os
from dateutil.relativedelta import relativedelta

import utils


class Klines:
    def __init__(self):
        """
        获取数据，数据入库
        """
        self.TABLE_NAME_KLINES = "klines"
        self.TABLE_NAME_RATE_HISTORY = "rate_history"
        # 币安API的基本URL
        self.BASE_URL = "https://fapi.binance.com"
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
        response = session.get(f"{self.BASE_URL}/fapi/v1/exchangeInfo")
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

    # 获取资金费率数据
    def get_funding_rate(
        self,
        start_time,
        end_time=int(datetime.datetime.now().timestamp() * 1000),
        symbol="BTCUSDT",
    ):
        session = requests.Session()
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "end_time": end_time,
            "limit": 1000,  # 最大限制
        }

        rate_list = []
        response = session.get(f"{self.BASE_URL}/fapi/v1/fundingRate", params=params)
        if response.status_code == 200:
            rate_list = response.json()
        else:
            print(f"获取资金费率历史数据失败，状态码：{response.status_code}")
        rate_df = pd.DataFrame(rate_list)
        rate_df.rename(
            columns={
                "fundingTime": "timestamp",
                "fundingRate": "rate",
                "markPrice": "mark_price",
            },
            inplace=True,
        )
        rate_df["time"] = (
            pd.to_datetime(rate_df["timestamp"], unit="ms").astype(str).str[:-4]
        )
        rate_df["time_symbol"] = rate_df["time"] + " " + rate_df["symbol"]
        return rate_df

    # 资金费率数据导入数据库
    def get_funding_rate_and_save_to_db(
        self,
        start_time,
        end_time=int(datetime.datetime.now().timestamp() * 1000),
        symbol="BTCUSDT",
    ):
        _data = self.get_funding_rate(
            start_time=start_time, end_time=end_time, symbol=symbol
        )
        cols = (
            "time_symbol",
            "symbol",
            "time",
            "timestamp",
            "rate",
            "mark_price",
        )
        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME_RATE_HISTORY}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_symbol TEXT UNIQUE,
            symbol TEXT,
            time TEXT,
            timestamp INTEGER,
            rate TEXT,
            mark_price TEXT)
            """
        )
        self.conn.commit()
        for x in _data.index:
            data_list = str(tuple([_data.loc[x, _col] for _col in cols]))
            self.cur.execute(
                f"INSERT OR IGNORE INTO {self.TABLE_NAME_RATE_HISTORY} {str(cols)} VALUES {data_list}"
            )
        self.conn.commit()

    # 获取k线数据
    def get_kline(
        self,
        start_time,
        end_time=int(datetime.datetime.now().timestamp() * 1000),
        interval="1m",
        symbol="BTCUSDT",
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
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "end_time": end_time,
            "limit": 1500,  # 最大限制
        }

        response = session.get(f"{self.BASE_URL}/fapi/v1/klines", params=params)
        if response.status_code == 200:
            kline_data_list = response.json()
        else:
            print(f"获取K线数据失败，状态码：{response.status_code}")

        # 将K线数据转换为DataFrame
        kline_df = pd.DataFrame(
            kline_data_list,
            columns=[
                "open_timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_timestamp",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )
        kline_df["open_time"] = pd.to_datetime(
            kline_df["open_timestamp"], unit="ms"
        ).astype(str)
        kline_df["close_time"] = pd.to_datetime(
            kline_df["close_timestamp"], unit="ms"
        ).astype(str)
        kline_df["open_time_symbol"] = kline_df["open_time"] + f" {symbol}"
        kline_df["pair"] = symbol
        return kline_df

    # k线交易数据导入数据库
    def get_data_and_save_to_db(self, start_time, interval="1m", symbol="BTCUSDT"):
        """
        # 开始时间
        start_time

        """
        print(
            symbol,
            "拿1500条(一天1440条), 开始时间：",
            datetime.datetime.fromtimestamp(start_time / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        _data = self.get_kline(start_time=start_time, interval=interval, symbol=symbol)
        cols = (
            "open_time_symbol",
            "open_time",
            "open_timestamp",
            "pair",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "close_timestamp",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        )
        self.cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME_KLINES}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            open_time_symbol TEXT UNIQUE,
            open_time TEXT,
            open_timestamp INTEGER,
            pair TEXT,
            open TEXT,
            high TEXT,
            low TEXT,
            close TEXT,
            volume TEXT,
            close_time TEXT,
            close_timestamp INTEGER,
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
                f"INSERT OR IGNORE INTO {self.TABLE_NAME_KLINES} {str(cols)} VALUES {data_list}"
            )
        self.conn.commit()

    # 获取数据库k线数据
    def get_db_data(self, pair="ALL", interval=""):
        """
        ### interval(获取多久的数据): '1h','1d','3d','1w','1m','1y',''
            ''则取全部
        """
        sql = f"SELECT * FROM {self.TABLE_NAME_KLINES}"
        if pair != "ALL":
            sql += f" WHERE pair='{pair}'"
        if interval != "":
            # 获取数据的时间段
            now = datetime.datetime.now().replace(second=0, microsecond=0)  # 精度到分钟
            time_delta = utils.get_time_delta(interval=interval)
            start_time = now - time_delta
            start_time_UTC = utils.to_UTC(start_time)
            print(f"从库中取{pair}的{start_time}及以后数据")
            print("start_time_UTC", start_time_UTC)
            # 库中存储时间均为UTC时间
            sql += f"AND open_time>='{start_time_UTC}'"

        _kline_data = pd.read_sql_query(sql, self.conn)
        return _kline_data
