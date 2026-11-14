"""
读取 4 个原始 CSV，合并后写入 MySQL 的 video_raw 表。
"""
import os
import pandas as pd
from sqlalchemy import create_engine

DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
DB_HOST = os.environ.get("MYSQL_HOST", "localhost")
DB_PORT = os.environ.get("MYSQL_PORT", "3306")
DB_NAME = os.environ.get("MYSQL_DB", "bilibili_food")

if not DB_PASSWORD:
    raise SystemExit(
        "未检测到数据库口令。请先设置环境变量 MYSQL_PASSWORD 再运行本脚本。\n"
        '  PowerShell:  $env:MYSQL_PASSWORD="你的口令"\n'
        '  Bash:        export MYSQL_PASSWORD="你的口令"'
    )

RAW_FILES = [
    "BiliBili_FOOD_Video_1.csv",
    "BiliBili_FOOD_Video_2.csv",
    "Bilibili_FOOD_Video_3.csv",
    "Bilibili_FOOD_Video_4.csv",
]
df = pd.concat(
    [pd.read_csv(f, encoding="utf-8") for f in RAW_FILES],
    ignore_index=True,
)
print("原始数据形状:", df.shape)

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

df.to_sql("video_raw", engine, if_exists="replace", index=False)

print("已导入 video_raw 表，共", len(df), "行")
