from decimal import Decimal
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from finta import TA


class BackTestEngine:
    def __init__(self, fee_pro=0.0005):
        # 初始化交易引擎
        self.fee_pro = fee_pro  # 交易手续费率

        self.positions = 0  # 仓位
        self.open_fee = 0  # 开仓交易费
        self.profit = 0  # 单次盈亏（比率）
        self.profit_total = 0  # 累计盈亏（比率）
        self.trades_df = pd.DataFrame(
            columns=[
                "created_at",
                "currency",
                "type_",
                "price",
                "quantity",
                "quantity_u",
                "profit",
                "profit_total",
                "mark",
            ]
        )  # 成交记录
        self.data = None  # 历史价格数据

    def load_data(self, data):
        # 载入历史价格数据
        self.data = data

    def execute_order(self, symbol, datetime, vol, price, action):
        """
        ### action: 'long','short','close'
        """
        cost = Decimal(price) * Decimal(vol)
        cost_abs = abs(Decimal(cost))
        fee = cost_abs * Decimal(self.fee_pro)  # 单次手续费
        self.positions = Decimal(self.positions) + Decimal(vol)
        if action == "close":
            trade_fee = Decimal(self.open_fee) + fee
            profit_money = cost_abs - self.open_money - trade_fee
            self.profit = round(profit_money / self.open_money, 4)
            self.profit_total += self.profit
        else:  # 开仓
            self.open_fee = fee
            self.open_money = cost_abs
            self.profit = ""

        currency = symbol[:-4]
        action_map = {"close": "平仓", "long": "买入", "short": "卖出"}
        __df = pd.DataFrame(
            [
                {
                    "created_at": datetime,
                    "currency": currency,
                    "type_": action,
                    "price": price,
                    "quantity": abs(vol),
                    "quantity_u": cost_abs,
                    "profit": self.profit,
                    "profit_total": float(self.profit_total),
                    "mark": f"<{currency}>{action_map[action]}",
                }
            ]
        )
        self.trades_df = pd.concat([self.trades_df, __df])  # 记录成交

    def clear_trades(self):
        self.trades_df = pd.DataFrame(
            columns=[
                "symbol",
                "datetime",
                "action",
                "cash",
                "positions",
                "vol",
                "price",
                "trade_fee",
                "profit",
            ]
        )

    # Strategy
    def s_sma169(self, symbol, take_profit_ratio=1.01):
        # 大于sma169买入，小于sma169或者到达止盈点卖出
        _df = self.data
        _df["sma169"] = TA.SMA(_df, 169)
        _df["pre_price"] = _df["close"].shift(1)

        take_profit_price = 0
        # stop_loss_price = 0

        for i, row in _df.iterrows():
            if i < 169 - 1:
                continue
            datetime = row["timestamp"]
            price = float(row["close"])
            pre_price = float(row["pre_price"])
            sma169 = float(row["sma169"])
            if pre_price < sma169 and price > sma169 and self.positions == 0:
                action = "long"
                vol = 1
                take_profit_price = price * take_profit_ratio
                self.execute_order(symbol, datetime, vol, price, action)
            elif (
                (pre_price < take_profit_price and price >= take_profit_price)
                or (pre_price >= sma169 and price < sma169)
            ) and self.positions > 0:
                action = "close"
                vol = -1
                self.execute_order(symbol, datetime, vol, price, action)

    # output
    def create_trade_data_json(self, file_name="docs/trade_data.json"):
        json_str = self.trades_df.to_json(orient="records")
        with open(file_name, "w") as file:
            file.write(json_str)

    def create_bar_chart(self):
        symbol = self.trades_df.iloc[0, 1]
        ax = self.trades_df.plot(x="created_at", y="profit_total", kind="bar")
        ax.bar(self.trades_df["created_at"], self.trades_df["profit_total"], width=0.5)
        font_path = "/System/Library/Fonts/Supplemental/Songti.ttc"
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = font_prop.get_name()
        plt.title(f"{symbol} 收益表", fontproperties=font_prop)
        plt.xlabel("时间", fontproperties=font_prop)
        plt.ylabel("总收益", fontproperties=font_prop)
        plt.xticks(rotation=60)
        plt.subplots_adjust(bottom=0.3)  # 调整底部边距
        plt.show()
