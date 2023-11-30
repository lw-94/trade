import datetime
import os

from dateutil.relativedelta import relativedelta
import pytz


def write_file(file_path, content):
    directory = os.path.dirname(file_path)
    # 创建目录（如果它们不存在）
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as file:
        file.write(content)


def get_time_delta(interval: str):
    num = int(interval[:-1])
    unit = interval[-1:]
    unit_map = {
        "s": relativedelta(seconds=num),
        "h": relativedelta(hours=num),
        "d": relativedelta(days=num),
        "w": relativedelta(weeks=num),
        "m": relativedelta(months=num),
        "y": relativedelta(years=num),
    }
    return unit_map[unit]


def to_UTC(time: datetime.datetime):
    # 将datetime对象转换为UTC时间
    utc_timezone = pytz.timezone("UTC")
    utc_datetime = time.astimezone(utc_timezone).strftime("%Y-%m-%d %H:%M:%S")
    return utc_datetime
