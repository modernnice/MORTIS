import pandas as pd
def _time_to_seconds(ts: pd.Timestamp) -> float:
    """
    将 pandas.Timestamp 转换为秒（浮点数）
    如果是时间差或单个时间点都可以处理
    """
    if isinstance(ts, pd.Timedelta):
        return ts.total_seconds()
    elif isinstance(ts, pd.Timestamp):
        # 如果是 Timestamp，只取当天的秒部分（时分秒）
        return ts.hour * 3600 + ts.minute * 60 + ts.second + ts.microsecond / 1e6
    else:
        raise TypeError(f"Unsupported type for timestamp: {type(ts)}")

def __seconds_to_str(seconds: float)-> str:
    """
    将秒转换为 HH:MM:SS.MS 格式
    """
    return pd.Timestamp(seconds, unit="s").strftime("%M:%S.%f")[:-3]
