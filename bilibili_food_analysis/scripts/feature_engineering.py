"""
特征工程脚本：构造互动率 + 关系分析所需的特征变量。

本脚本产出：
1. 互动率（核心 Y 变量）—— 关系分析的目标
2. 标签数量、标题长度、介绍长度（X 变量）
3. 发布时间段、是否工作日（X 变量）
"""
import pandas as pd
import re

# ============ 1. 读取清洗后的数据 ============
df = pd.read_csv("bilibili_food_cleaned.csv", encoding="utf-8-sig")
print("读取:", df.shape)

# ============ 2. 构造互动率（核心 Y 变量）============
# 互动率 = (点赞 + 投币 + 收藏 + 分享 + 弹幕 + 评论) / 播放
# 含义：每一次播放平均带来多少次互动，衡量内容的互动质量。
interactions = df["点赞"] + df["投币"] + df["收藏"] + df["分享"] + df["弹幕"] + df["评论数"]
df["互动率"] = interactions / df["播放"]

# 播放为 0 的视频会除出无穷大，替换成 NaN（这些是无效样本）
df["互动率"] = df["互动率"].replace([float("inf"), float("-inf")], None)

print("\n互动率分布:")
print(df["互动率"].describe().round(5))

# ============ 3. 特征工程（X 变量）============

# 3.1 标签数量：标签列用换行/逗号分隔，数标签个数
df["标签数量"] = df["标签"].fillna("").apply(
    lambda x: len([t for t in re.split(r"[\n,，]", str(x)) if t.strip()])
)

# 3.2 标题长度：标题字符数
df["标题长度"] = df["标题"].astype(str).str.len()

# 3.3 介绍长度：视频介绍字符数
df["介绍长度"] = df["视频介绍"].astype(str).str.len()

# 3.4 发布时间段：从发布时间提取小时，切成 4 段
df["发布时间_dt"] = pd.to_datetime(df["发布时间"], errors="coerce") # 把文字格式转成 datetime
df["小时"] = df["发布时间_dt"].dt.hour

def hour_to_segment(h):
    if pd.isna(h):
        return "未知"
    if 0 <= h < 6:
        return "凌晨"
    elif 6 <= h < 12:
        return "上午"
    elif 12 <= h < 18:
        return "下午"
    else:
        return "晚上"

df["时段"] = df["小时"].apply(hour_to_segment)

# 3.5 是否工作日：从日期提取星期
df["星期"] = df["发布时间_dt"].dt.dayofweek  # 0=周一 ... 6=周日
df["是否工作日"] = df["星期"].apply(lambda x: "工作日" if x < 5 else "周末")

# ============ 4. 核对新特征 ============
print("\n=== 新特征分布 ===")
print("标签数量: 均值", round(df["标签数量"].mean(), 4), "中位数", df["标签数量"].median())
print("标题长度: 均值", round(df["标题长度"].mean(), 4), "中位数", df["标题长度"].median())
print("介绍长度: 均值", round(df["介绍长度"].mean(), 4), "中位数", df["介绍长度"].median())
print("\n时段分布:")
print(df["时段"].value_counts())
print("\n工作日/周末分布:")
print(df["是否工作日"].value_counts())

# ============ 5. 保存 ============
df.to_csv("bilibili_food_features.csv", index=False, encoding="utf-8-sig")
print("\n 已保存 bilibili_food_features.csv，共", len(df), "行 ×", len(df.columns), "列")
