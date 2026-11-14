"""
依据关键数据查询结果的 6 条质检结论：
1. 合并 4 个 CSV 后存在大量重复视频 → 去重
2. 评论数大量缺失 → 填 0
3. 总播放数含「万」单位 → 换算（×10000）
4. 点赞/金币/收藏/分享列混入「点赞/投币」等按钮文字 → 按 0 处理
5. 播放为 0 的视频 → 互动率记为 inf（后续分析时过滤）
6. 时间格式无异常 → 无需处理

处理 6 个指标列：总播放数、总弹幕数、点赞数、金币数、收藏量、分享数。
"""
import pandas as pd
import glob
import re

# 1. 读取合并 4 个原始 CSV
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
print("合并后形状:", df.shape)

# 2. 去重，按所有列都相同判定重复
before = len(df)
df = df.drop_duplicates(keep="first")
print(f"去重：{before} → {len(df)}（删除 {before - len(df)} 条重复）")

# 3. 定义清洗函数：单个值 → 数字
def parse_num(s):
    """从中文文本中提取数值，支持“万”单位，提取不到返回 0。"""
    if pd.isna(s):
        return 0.0
    s = str(s)
    # 匹配“数字（可含小数）+ 万?”的模式，如 '19.4万' 或 '54'
    m = re.search(r"(\d+(?:\.\d+)?)\s*万?", s)
    if not m:
        return 0.0
    num = float(m.group(1))
    # 含“万”则乘以 10000
    if "万" in s:
        num *= 10000
    return num

# 4. 清洗 6 个指标列
col_map = {
    "总播放数": "播放",
    "总弹幕数": "弹幕",
    "点赞数": "点赞",
    "金币数": "投币",
    "收藏量": "收藏",
    "分享数": "分享",
}
for old, new in col_map.items():
    df[new] = df[old].apply(parse_num)

# 5. 评论数缺失填 0
df["评论数"] = df["评论数"].fillna(0)

# 6. 核对：抽几行对比原列和新列
print("\n=== 抽样核对（原值 → 清洗后）===")
sample = df.sample(5, random_state=42)
for _, row in sample.iterrows():
    print(f"  播放: {row['总播放数']!r:28} → {row['播放']:.0f}")
    print(f"  点赞: {row['点赞数']!r:28} → {row['点赞']:.0f}")

# 7. 统计清洗结果
print("\n=== 清洗后统计===")
for new in ["播放", "弹幕", "点赞", "投币", "收藏", "分享"]:
    print(f"  {new}: min={df[new].min():.0f}, max={df[new].max():.0f}, "
          f"mean={df[new].mean():.1f}, 中位数={df[new].median():.0f}")

# 8. 保存清洗后的数据
df.to_csv("bilibili_food_cleaned.csv", index=False, encoding="utf-8-sig")
print("\n 已保存 bilibili_food_cleaned.csv，共", len(df), "行 ×", len(df.columns), "列")
