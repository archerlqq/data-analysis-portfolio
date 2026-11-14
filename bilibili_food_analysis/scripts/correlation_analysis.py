"""
关系探索：相关系数分析
==========================：
1. 只保留 播放 >= 1000 的样本 —— 小播放视频的互动率是分母过小的虚高值，
   会严重污染相关系数（播放<100 的视频互动率均值 1.4，中位数仅 0.08）。
2. 同时算 Pearson 和 Spearman —— 播放量是极端长尾分布（中位数 8721、最大值 684 万），
   Pearson 对极端值敏感，Spearman（秩相关）更稳健。
3. 对播放量做 log 变换后再算一次 —— 长尾数据取对数后接近正态，Pearson 才有意义。
4. 互动指标的绝对值（点赞/投币/...）之间用 Pearson 即可，它们是数量。
"""
import pandas as pd
import numpy as np

INPUT = "bilibili_food_features.csv"
OUTPUT = "correlation_results.txt"

lines = []
def log(s=""):
    print(s)
    lines.append(str(s))

# ============================================================
# 0. 读取与样本筛选
# ============================================================
df = pd.read_csv(INPUT, encoding="utf-8-sig")

# 互动率转数值（防止有残留的非数值）
df["互动率"] = pd.to_numeric(df["互动率"], errors="coerce")

before = len(df)
# 筛选条件：播放>=1000（剔除分母过小的噪声）+ 互动率非空 + 排除时段未知
df = df[df["播放"] >= 1000]
df = df[df["互动率"].notna()]
df = df[df["时段"] != "未知"]

log("=" * 70)
log("相关系数分析（样本：播放 >= 1000）")
log("=" * 70)
log(f"原始样本 {before} 行 → 分析样本 {len(df)} 行（占比 {len(df)/before*100:.1f}%）")
log(f"播放量：中位数 {df['播放'].median():.0f}，均值 {df['播放'].mean():.0f}")
log(f"互动率：中位数 {df['互动率'].median():.4f}，均值 {df['互动率'].mean():.4f}")
log()

# 对播放量取对数（长尾数据常用处理）
df["log播放"] = np.log10(df["播放"].clip(lower=1))

# ============================================================
# 1. 内容特征 vs 播放量
# ============================================================
log("-" * 70)
log("1. 内容特征 vs 播放量")
log("-" * 70)
log(f"{'特征':<10}{'Pearson':>12}{'Spearman':>12}   解读")
log("-" * 70)

feat_pairs = [
    ("标签数量", "log播放"),   # 标签数与播放：用 log 播放，避免极端值主导
    ("标题长度", "log播放"),
    ("介绍长度", "log播放"),
]
interpret = {
    "标签数量": "标签多的视频播放量略高，但强度很弱",
    "标题长度": "标题长度与播放基本无关",
    "介绍长度": "介绍长度与播放基本无关",
}
for feat, target in feat_pairs:
    sub = df[[feat, target]].dropna()
    p = sub[feat].corr(sub[target], method="pearson")
    s = sub[feat].corr(sub[target], method="spearman")
    log(f"{feat:<10}{p:>12.4f}{s:>12.4f}   {interpret.get(feat,'')}")

# 原始播放量也报一遍（对比 log 后的差异，说明长尾的影响）
log()
log("对照：不做 log 变换、直接用原始播放量：")
for feat, _ in feat_pairs:
    sub = df[[feat, "播放"]].dropna()
    p = sub[feat].corr(sub["播放"], method="pearson")
    s = sub[feat].corr(sub["播放"], method="spearman")
    log(f"  {feat:<8} Pearson={p:>8.4f}  Spearman={s:>8.4f}")
log()

# ============================================================
# 2. 标签数量 vs 互动率
# ============================================================
log("-" * 70)
log("2. 内容特征 vs 互动率")
log("-" * 70)
for feat in ["标签数量", "标题长度", "介绍长度"]:
    sub = df[[feat, "互动率"]].dropna()
    p = sub[feat].corr(sub["互动率"], method="pearson")
    s = sub[feat].corr(sub["互动率"], method="spearman")
    log(f"  {feat:<8} Pearson={p:>8.4f}  Spearman={s:>8.4f}  (n={len(sub)})")
log()

# ============================================================
# 3. 互动指标之间的相关矩阵
# ============================================================
log("-" * 70)
log("3. 互动指标相关矩阵（Pearson，绝对值）")
log("-" * 70)
interact_cols = ["播放", "弹幕", "点赞", "投币", "收藏", "分享", "评论数"]
corr_matrix = df[interact_cols].corr(method="pearson").round(3)
log(corr_matrix.to_string())
log()

log("补充：上述指标取 log10 后的相关矩阵（消除数量级差异）：")
log_df = df[interact_cols].apply(lambda s: np.log10(s.clip(lower=0) + 1))
log(log_df.corr(method="pearson").round(3).to_string())
log()

# ============================================================
# 4. 效应量：标签档位之间的相对差异
# ============================================================
log("-" * 70)
log("4. 效应量：标签档位的互动率差异")
log("-" * 70)
df["标签档"] = pd.cut(df["标签数量"], bins=[-1, 3, 7, 99], labels=["0-3", "4-7", "8+"])
grp = df.groupby("标签档", observed=True)["互动率"].agg(
    样本数="size", 均值="mean", 中位数="median"
).round(4)
log(grp.to_string())

base_median = grp.loc["0-3", "中位数"]
base_mean = grp.loc["0-3", "均值"]
log()
for lv in ["4-7", "8+"]:
    lift_med = (grp.loc[lv, "中位数"] - base_median) / base_median * 100
    lift_mean = (grp.loc[lv, "均值"] - base_mean) / base_mean * 100
    log(f"  {lv} 标签 vs 0-3 标签：中位数提升 {lift_med:+.1f}%，均值提升 {lift_mean:+.1f}%")
log()

# ============================================================
# 5. 保存结果
# ============================================================
with open(OUTPUT, "w", encoding="utf-8-sig") as f:
    f.write("\n".join(lines))
print(f"\n✅ 结果已保存到 {OUTPUT}")
