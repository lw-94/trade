import pandas as pd
import matplotlib.pyplot as plt


class BackTestEngine:
    def __init__(self, fee_pro=0.0005):
        # 初始化交易引擎
        self.cash = 0
        self.positions = 0  # 投资组合，包括现金
        self.trade_fee = 0  # 累计交易成本
        self.profit = 0  # 累计盈亏
        self.fee_pro = fee_pro  # 交易手续费率
        self.trades_df = pd.DataFrame(
            columns=[
                "symbol",
                "datetime",
                "cash",
                "positions",
                "vol",
                "price",
                "trade_fee",
                "profit",
            ]
        )  # 成交记录
        self.data = None  # 历史价格数据

    def load_data(self, data):
        # 载入历史价格数据
        self.data = data

    def execute_order(self, symbol, datetime, vol, price):
        cost = price * vol
        self.trade_fee = self.trade_fee + abs(cost) * self.fee_pro  # 更新累计手续费
        self.cash = self.cash - cost - abs(cost) * self.fee_pro  # 更新现金
        self.positions = self.positions + vol
        self.profit = self.cash + self.positions * price

        __df = pd.DataFrame(
            [
                {
                    "symbol": symbol,
                    "datetime": datetime,
                    "cash": self.cash,
                    "positions": self.positions,
                    "vol": vol,
                    "price": price,
                    "trade_fee": self.trade_fee,
                    "profit": self.profit,
                }
            ]
        )
        self.trades_df = pd.concat([self.trades_df, __df])  # 记录成交

    def create_trade_data_json(self, file_name="../docs/trade_data.json"):
        json_str = self.trades_df.to_json(orient="records")
        with open(file_name, "w") as file:
            file.write(json_str)

    def create_bar_chart(self):
        symbol = self.trades_df.iloc[0, 0]
        ax = self.trades_df.plot(x="datetime", y="profit", kind="bar")
        ax.bar(self.trades_df["datetime"], self.trades_df["profit"], width=0.5)
        plt.rcParams["font.family"] = "STHeiti"
        plt.title(f"{symbol} chart")
        plt.xlabel("datetime")
        plt.ylabel("profit")
        plt.xticks(rotation=60)
        plt.subplots_adjust(bottom=0.3)  # 调整底部边距
        plt.show()
