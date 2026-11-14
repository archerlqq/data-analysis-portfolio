"""
生成 4 张分析图
=================================
四张图分别回答：
图1  播放量分布 —— 这个平台的内容是长尾结构吗？
图2  过滤前 vs 过滤后 —— 不控制播放量会得出什么错误结论？
图3  播放区间 × 标签档 热力图 —— 控制播放量后，标签效应还在吗？
图4  UP 主产量 vs 播放/互动率 —— 产量带来规模，但带来互动吗？
"""
import os
import numpy as np
import pandas as pd
import matplotlib
         
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
matplotlib.use("Agg") 
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False  
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 150
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 0. 读取数据，准备两套样本
# ============================================================
df = pd.read_csv("bilibili_food_features.csv", encoding="utf-8-sig")
df["互动率"] = pd.to_numeric(df["互动率"], errors="coerce")

# 全样本（仅剔除播放=0 与互动率为空）
d_all = df[(df["播放"] > 0) & df["互动率"].notna()].copy()

# 分析样本（播放>=1000）
d_ok = d_all[d_all["播放"] >= 1000].copy()

d_all["标签档"] = pd.cut(d_all["标签数量"], bins=[-1, 3, 7, 99], labels=["0-3", "4-7", "8+"])
d_ok["标签档"] = pd.cut(d_ok["标签数量"], bins=[-1, 3, 7, 99], labels=["0-3", "4-7", "8+"])

print(f"全样本 {len(d_all)} 行；分析样本 {len(d_ok)} 行")

# UP 主产量分层
def tier(n):
    if n == 1:
        return "1篇"
    elif n <= 5:
        return "2-5篇"
    elif n <= 20:
        return "6-20篇"
    else:
        return "20+篇"

up_cnt = d_ok.groupby("发布者")["播放"].size()
d_ok["UP产量档"] = d_ok["发布者"].map(up_cnt).apply(tier)
TIER_ORDER = ["1篇", "2-5篇", "6-20篇", "20+篇"]


# ============================================================
# 图 1：播放量分布（对数坐标）—— 证明长尾结构
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))

plays = d_all["播放"].clip(lower=1)
bins = np.logspace(0, np.log10(plays.max()), 60)      # 对数等距分箱
ax.hist(plays, bins=bins, color="#4C72B0", edgecolor="white", linewidth=0.5, alpha=0.85)

ax.set_xscale("log")
ax.set_xlabel("播放量（对数坐标）", fontsize=11)
ax.set_ylabel("视频数量", fontsize=11)
ax.set_title("图1  B站美食区视频播放量分布：典型的长尾结构", fontsize=13, fontweight="bold", pad=14)

# 标注中位数与均值
med, mean = plays.median(), plays.mean()
ax.axvline(med, color="#C44E52", linestyle="--", linewidth=2, label=f"中位数 = {med:,.0f}")
ax.axvline(mean, color="#DD8452", linestyle="--", linewidth=2, label=f"均值 = {mean:,.0f}")
ax.legend(fontsize=10, loc="upper right")

ax.text(0.98, 0.62,
        f"中位数仅为均值的 {med/mean*100:.0f}%\n说明绝大多数视频播放量很低，\n均值由极少数爆款拉动",
        transform=ax.transAxes, ha="right", va="top", fontsize=10,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF4E6", edgecolor="#DD8452"))

ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "图1_播放量长尾分布.png"), bbox_inches="tight")
plt.close()
print("图1 已生成")


# ============================================================
# 图 2：过滤前 vs 过滤后 
# ============================================================
# 三个维度各自算初版（全样本均值）与修正版（播放>=1000 均值）
def mean_by(data, col, order):
    s = data.groupby(col, observed=True)["互动率"].mean().reindex(order)
    return s

FACTORS = [
    ("标签档", ["0-3", "4-7", "8+"], "标签数量"),
    ("时段", ["凌晨", "上午", "下午", "晚上"], "发布时段"),
    ("UP产量档", TIER_ORDER, "UP主产量"),
]

up_cnt_all = d_all.groupby("发布者")["播放"].size()
d_all["UP产量档"] = d_all["发布者"].map(up_cnt_all).apply(tier)

fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
for ax, (col, order, title) in zip(axes, FACTORS):
    before = mean_by(d_all, col, order)
    after = mean_by(d_ok, col, order)

    x = np.arange(len(order))
    w = 0.38
    ax.bar(x - w/2, before.values, w, label="未控制播放量", color="#C44E52", alpha=0.85)
    ax.bar(x + w/2, after.values, w, label="播放≥1000", color="#55A868", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(order, fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_ylabel("平均互动率", fontsize=10)
    ax.legend(fontsize=9)

    for xi, v in zip(x - w/2, before.values):
        if not np.isnan(v):
            ax.text(xi, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8, color="#8B2E30")
    for xi, v in zip(x + w/2, after.values):
        if not np.isnan(v):
            ax.text(xi, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8, color="#2F6B44")

fig.suptitle("图2  不控制播放量会严重夸大差异（红=初版结论，绿=控制后的真实差异）",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "图2_过滤前后对比.png"), bbox_inches="tight")
plt.close()
print("图2 已生成")


# ============================================================
# 图 3：播放区间 × 标签档 热力图 —— 控制变量后的稳健效应
# ============================================================
d_ok["播放箱"] = pd.cut(d_ok["播放"], bins=[1000, 10000, 100000, np.inf],
                        labels=["1k-1w", "1w-10w", ">10w"])

pivot = d_ok.pivot_table(index="播放箱", columns="标签档",
                         values="互动率", aggfunc="median", observed=True)
counts = d_ok.pivot_table(index="播放箱", columns="标签档",
                          values="互动率", aggfunc="size", observed=True)

fig, ax = plt.subplots(figsize=(7.6, 4.6))
im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")

ax.set_xticks(np.arange(pivot.shape[1]))
ax.set_xticklabels([f"{c} 标签" for c in pivot.columns], fontsize=10)
ax.set_yticks(np.arange(pivot.shape[0]))
ax.set_yticklabels(pivot.index, fontsize=10)
ax.set_xlabel("标签数量分档", fontsize=11)
ax.set_ylabel("播放量区间", fontsize=11)
ax.set_title("图3  控制播放量后，标签越多互动率越高（单元格=互动率中位数）",
             fontsize=12, fontweight="bold", pad=12)

for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        v = pivot.values[i, j]
        n = counts.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.3f}\n(n={int(n)})", ha="center", va="center",
                    fontsize=9, color="black")

ax.grid(False)
plt.colorbar(im, ax=ax, label="互动率中位数")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "图3_标签与播放交叉热力图.png"), bbox_inches="tight")
plt.close()
print("图3 已生成")


# ============================================================
# 图 4：UP 主产量 vs 单条播放 / 互动率 —— 规模与互动的分离
# ============================================================
agg = d_ok.groupby("UP产量档").agg(
    单条平均播放=("播放", "mean"),
    互动率中位数=("互动率", "median"),
    视频数=("播放", "size"),
).reindex(TIER_ORDER)

fig, ax1 = plt.subplots(figsize=(9, 5.2))
x = np.arange(len(TIER_ORDER))

bars = ax1.bar(x, agg["单条平均播放"], color="#4C72B0", alpha=0.8, label="单条平均播放（左轴）")
ax1.set_ylabel("单条平均播放量", fontsize=11, color="#4C72B0")
ax1.tick_params(axis="y", labelcolor="#4C72B0")
ax1.set_xticks(x)
ax1.set_xticklabels(TIER_ORDER, fontsize=10)
ax1.set_xlabel("UP 主投稿数分层", fontsize=11)
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/10000:.0f}万"))

# 柱子上标播放值
for xi, v in zip(x, agg["单条平均播放"]):
    ax1.text(xi, v, f"{v/10000:.1f}万", ha="center", va="bottom", fontsize=9, color="#2C4A6E")

# 右轴：互动率
ax2 = ax1.twinx()
ax2.plot(x, agg["互动率中位数"], color="#C44E52", marker="o", linewidth=2.5,
         markersize=8, label="互动率中位数（右轴）")
ax2.set_ylabel("互动率中位数", fontsize=11, color="#C44E52")
ax2.tick_params(axis="y", labelcolor="#C44E52")
ax2.grid(False)

# 折线上标数值
for xi, v in zip(x, agg["互动率中位数"]):
    ax2.text(xi, v, f"{v:.3f}", ha="center", va="top", fontsize=9, color="#8B2E30")

ax1.set_title("图4  产量带来播放规模，但不带来互动质量",
              fontsize=13, fontweight="bold", pad=14)

# 合并两个轴的图例
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "图4_产量与规模分离.png"), bbox_inches="tight")
plt.close()
print("图4 已生成")

print(f"\n全部完成，图片保存在 {os.path.abspath(OUT_DIR)}")
