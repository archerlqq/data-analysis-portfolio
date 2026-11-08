import pandas as pd

pd.set_option('display.max_rows', None)      # 不限制最大行数
pd.set_option('display.max_columns', None)   # 不限制最大列数
pd.set_option('display.width', None)         # 终端宽度不限制换行
pd.set_option('display.max_colwidth', None) # 单元格内容不截断

df = pd.read_csv("customer_shopping_behavior.csv", encoding="utf-8-sig")

print("===== 前5行数据 =====")
print(df.head(5))

print("\n===== 数据类型和缺失概览 df.info() =====")
df.info()  # info自带打印

print("\n===== 全量描述统计 describe =====")
print(df.describe(include="all"))

print("\n===== 每列缺失值数量 isnull.sum =====")
print(df.isnull().sum())
