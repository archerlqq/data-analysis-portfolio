# -*- coding: utf-8 -*-
"""
1. 列名转 snake_case（purchase_amount_(usd) -> purchase_amount）
2. 缺失值：Review Rating 按「品类中位数」填补
3. 删冗余列：Promo Code Used 与 Discount Applied 完全一致，删 Promo Code Used
4. 新增 age_group：按年龄四等分（qcut）
5. 落库成 customer 表
"""
import os

import pandas as pd
from sqlalchemy import create_engine

# ============================
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")  # MySQL 密码      
DB_NAME = "customer_analysis"  # 数据库名
# ============================

# 口令为空时提前报错，避免带着空口令连接、报错信息难以定位
if not MYSQL_PASSWORD:
    raise SystemExit("未检测到环境变量 MYSQL_PASSWORD，请先设置数据库口令后重试")

# 1. 读原始数据
df = pd.read_csv("customer_shopping_behavior.csv", encoding="utf-8-sig")

# 2. 列名转 snake_case（对齐原项目）
df.columns = df.columns.str.lower().str.replace(" ", "_")
df = df.rename(columns={"purchase_amount_(usd)": "purchase_amount"})

# 3. 37个缺失值：Review Rating 按品类中位数填补，分层中位数比全局中位数更严谨
#    注意：groupby().transform 会让每一行拿到「自己所在品类」的中位数
df["review_rating"] = df.groupby("category")["review_rating"].transform(
    lambda x: x.fillna(x.median())
)

# 4. 删冗余列：promo_code_used 与 discount_applied 完全一致，删掉前者
df = df.drop(columns=["promo_code_used"])

# 5. 新增 age_group：按年龄四等分
labels = ["Young Adult", "Adult", "Middle-aged", "Senior"]
df["age_group"] = pd.qcut(df["age"], q=4, labels=labels)

# 6. 新增 purchase_frequency_days：将 frequency_of_purchases 转为天数
frequency_mapping = {
    "Weekly": 7, "Fortnightly": 14, "Bi-Weekly": 14,
    "Monthly": 30, "Quarterly": 90, "Every 3 Months": 90, "Annually": 365
}
df["purchase_frequency_days"] = df["frequency_of_purchases"].map(frequency_mapping)


# 7. 打印核对
print("清洗后形状：", df.shape)
print("列名：", list(df.columns))
print("Review Rating 剩余缺失：", df["review_rating"].isna().sum())
print("age_group 分布：")
print(df["age_group"].value_counts().sort_index())

# 7. 落库
engine = create_engine(
    f"mysql+pymysql://root:{MYSQL_PASSWORD}@localhost:3306/{DB_NAME}?charset=utf8mb4"
)
df.to_sql("customer", engine, if_exists="replace", index=False)
print("\n✅ 已写入 customer 表，共", len(df), "行 ×", len(df.columns), "列")
