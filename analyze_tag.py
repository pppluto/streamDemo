# -*- coding: utf-8 -*-
"""对 tag.xlsx Sheet2 做数据概览 + 相关性分析（含点消、拖消、目标物品），并输出结论文档与 CSV。"""
import pandas as pd
import numpy as np

FILE = "tag.xlsx"
OUT_PREFIX = "tag"
TAG_COLS = ["点消", "拖消", "目标物品"]

df = pd.read_excel(FILE, sheet_name="Sheet2", engine="openpyxl")
# 统一标签列名（Sheet2 第 3～5 列为点消、拖消、目标物品）
if len(df.columns) >= 5:
    df = df.rename(columns={
        df.columns[2]: "点消",
        df.columns[3]: "拖消",
        df.columns[4]: "目标物品",
    })

numeric = df.select_dtypes(include=[np.number])
numeric = numeric.dropna(axis=1, how="all")
numeric = numeric.loc[:, numeric.nunique() > 1]

# 业务汇总
total_imp = df["Impressions"].sum()
total_spend = df["Spend"].sum()
total_cta = df["CTA clicked"].sum()
n_unique_html = df["HTML"].nunique()
avg_ctr = df["CTA click rate"].mean() * 100
avg_cvr = df["Unique redirects rate"].mean() * 100
avg_ivr = df["Unique interactions rate"].mean() * 100
avg_completion = df["HTML completion rate"].mean() * 100
n_imp_1k = (df["Impressions"] > 1000).sum()
n_imp_10k = (df["Impressions"] > 10000).sum()
n_cta_pos = (df["CTA clicked"] > 0).sum()
have_result = df[(df["Challenge solved"] > 50) & (df["Challenge failed"] > 50)]
free_play = df[(df["Challenge solved"] == 0) & (df["Challenge failed"] == 0)]

# 相关性
corr_pearson = numeric.corr(method="pearson")
corr_spearman = numeric.corr(method="spearman")
corr_pearson.to_csv(f"{OUT_PREFIX}_correlation_pearson.csv", encoding="utf-8-sig")
corr_spearman.to_csv(f"{OUT_PREFIX}_correlation_spearman.csv", encoding="utf-8-sig")

n = len(corr_pearson)
pairs = []
for i in range(n):
    for j in range(i + 1, n):
        a, b = corr_pearson.columns[i], corr_pearson.columns[j]
        p_val = corr_pearson.iloc[i, j]
        s_val = corr_spearman.iloc[i, j]
        pairs.append((a, b, float(p_val), float(s_val)))
pairs_sorted = sorted(pairs, key=lambda x: abs(x[2]), reverse=True)
rate_cols = [c for c in numeric.columns if "rate" in c.lower()]
rate_pairs = [(a, b, p, s) for a, b, p, s in pairs_sorted if a in rate_cols and b in rate_cols and abs(p) >= 0.5]

# 点消、拖消、目标物品 与核心指标的相关
tag_pairs = [(a, b, p, s) for a, b, p, s in pairs_sorted if (a in TAG_COLS or b in TAG_COLS) and abs(p) >= 0.2]

# 写入 Markdown 报告
lines = [
    f"# {FILE} 数据分析结论",
    "",
    f"基于 **{FILE}**：{len(df)} 行、{len(df.columns)} 列。数值列参与相关性的共 {numeric.shape[1]} 列。",
    "",
    "---",
    "",
    "## 一、数据概览",
    "",
    "| 项目 | 数值 |",
    "|------|------|",
    f"| 总行数 | {len(df)} |",
    f"| 唯一素材数 (HTML) | {n_unique_html} |",
    f"| 总展示量 (Impressions) | {total_imp:,.0f} |",
    f"| 总花费 (Spend) | ${total_spend:,.2f} |",
    f"| 总点击 (CTA clicked) | {total_cta:,.0f} |",
    f"| 平均点击率 (CTR) | {avg_ctr:.2f}% |",
    f"| 平均跳转转化率 (CVR) | {avg_cvr:.2f}% |",
    f"| 平均互动率 (IVR) | {avg_ivr:.2f}% |",
    f"| 平均完播率 | {avg_completion:.2f}% |",
    f"| 展示量 > 1000 的行数 | {n_imp_1k} |",
    f"| 展示量 > 10000 的行数 | {n_imp_10k} |",
    f"| CTA clicked > 0 的行数 | {n_cta_pos} |",
    f"| 有明确游戏结果 (solved>50 & failed>50) | {len(have_result)} |",
    f"| 限时自由玩 (solved=0 & failed=0) | {len(free_play)} |",
    "",
]

# 点消、拖消、目标物品 描述（并入概览表）
for col in TAG_COLS:
    if col not in df.columns:
        continue
    s = df[col].dropna()
    lines.append(f"| **{col}** 非空数 / 均值 / 标准差 | {len(s)} / {s.mean():.3f} / {s.std():.3f} |")

lines.extend([
    "---",
    "",
    "## 二、标签列：点消、拖消、目标物品",
    "",
    "以下为这三列与其它数值指标的相关系数（|Pearson| ≥ 0.2），便于观察标签与消耗、转化、游戏行为的关系。",
    "",
    "| 指标 A | 指标 B | Pearson | Spearman |",
    "|--------|--------|---------|----------|",
])
for a, b, p, s in tag_pairs[:25]:
    lines.append(f"| {a} | {b} | {p:.3f} | {s:.3f} |")
lines.extend([
    "",
    "---",
    "",
    "## 三、相关性分析（全表）",
    "",
    f"完整相关矩阵已导出：`{OUT_PREFIX}_correlation_pearson.csv`、`{OUT_PREFIX}_correlation_spearman.csv`。",
    "",
    "### 率指标之间强相关 (|Pearson| ≥ 0.5)",
    "",
    "| 指标 A | 指标 B | Pearson | Spearman |",
    "|--------|--------|---------|----------|",
])
for a, b, p, s in rate_pairs[:20]:
    lines.append(f"| {a} | {b} | {p:.3f} | {s:.3f} |")
lines.extend([
    "",
    "### 全表最强相关对 (按 |Pearson| 前 15 对)",
    "",
    "| 指标 A | 指标 B | Pearson | Spearman |",
    "|--------|--------|---------|----------|",
])
for a, b, p, s in pairs_sorted[:15]:
    lines.append(f"| {a} | {b} | {p:.3f} | {s:.3f} |")
lines.extend([
    "",
    "---",
    "",
    "## 四、与 sksx 的对比说明",
    "",
    "若需与 sksx.xlsx 对比，可在 Streamlit 侧栏切换「数据表」分别查看；相关性结论结构一致，数值会随 tag.xlsx 数据更新而变化。",
    "",
])

with open(f"{OUT_PREFIX}_分析结论.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Done: {OUT_PREFIX}_分析结论.md, {OUT_PREFIX}_correlation_pearson.csv, {OUT_PREFIX}_correlation_spearman.csv")
