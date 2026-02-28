# -*- coding: utf-8 -*-
"""排除极值素材后，对 tag.xlsx Sheet2 重新做概览、标签对比与相关性分析，并输出报告。"""
import pandas as pd
import numpy as np

FILE = "tag.xlsx"
OUT_MD = "数据分析报告_排除极值.md"
OUT_PREFIX = "tag_no_outliers"
TAG_COLS = ["点消", "拖消", "目标物品"]

# 极值判定：按展示量 Impressions 的 IQR 方法，超出 [Q1-1.5*IQR, Q3+1.5*IQR] 视为极值
def flag_outliers_iqr(series, k=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return pd.Series(False, index=series.index)
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper)

df = pd.read_excel(FILE, sheet_name="Sheet2", engine="openpyxl")
if len(df.columns) >= 5:
    df = df.rename(columns={
        df.columns[2]: "点消",
        df.columns[3]: "拖消",
        df.columns[4]: "目标物品",
    })

# 按 Impressions 标出极值
imp = df["Impressions"].dropna()
outlier_mask = flag_outliers_iqr(df["Impressions"])
excluded = df.loc[outlier_mask].copy()
df_in = df.loc[~outlier_mask].copy()
n_excluded = outlier_mask.sum()
excluded_names = excluded["HTML"].tolist() if "HTML" in excluded.columns else []

# 数值列（排除极值后）
numeric = df_in.select_dtypes(include=[np.number])
numeric = numeric.dropna(axis=1, how="all")
numeric = numeric.loc[:, numeric.nunique() > 1]

# 业务汇总（排除极值后）
total_imp = df_in["Impressions"].sum()
total_spend = df_in["Spend"].sum()
total_cta = df_in["CTA clicked"].sum()
n_unique_html = df_in["HTML"].nunique()
avg_ctr = df_in["CTA click rate"].mean() * 100
avg_cvr = df_in["Unique redirects rate"].mean() * 100
avg_ivr = df_in["Unique interactions rate"].mean() * 100
avg_completion = df_in["HTML completion rate"].mean() * 100
n_imp_1k = (df_in["Impressions"] > 1000).sum()
n_imp_10k = (df_in["Impressions"] > 10000).sum()
n_cta_pos = (df_in["CTA clicked"] > 0).sum()
have_result = df_in[(df_in["Challenge solved"] > 50) & (df_in["Challenge failed"] > 50)]
free_play = df_in[(df_in["Challenge solved"] == 0) & (df_in["Challenge failed"] == 0)]

# 相关性（排除极值后）
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
tag_pairs = [(a, b, p, s) for a, b, p, s in pairs_sorted if (a in TAG_COLS or b in TAG_COLS) and abs(p) >= 0.2]

# 标签对比（排除极值后）：与 tag_label_compare 相同逻辑
for c in TAG_COLS:
    if c in df_in.columns:
        df_in[c] = pd.to_numeric(df_in[c], errors="coerce")

def assign_tag(row):
    if row.get("目标物品") == 1:
        return "目标物品"
    if row.get("点消") == 1:
        return "点消"
    if row.get("拖消") == 1:
        return "拖消"
    return "未标注"

df_in["_tag"] = df_in.apply(assign_tag, axis=1)
metrics = [
    "Impressions", "Spend", "CTA clicked", "CTA click rate",
    "Unique redirects rate", "HTML completion rate", "Challenge solved rate",
    "Average duration", "Runtime error rate",
]
metrics = [m for m in metrics if m in df_in.columns]
overall = df_in[metrics].mean()
ratio_rows = []
for tag in ["点消", "拖消", "目标物品"]:
    sub_df = df_in[df_in["_tag"] == tag]
    if len(sub_df) == 0:
        continue
    sub = sub_df[metrics].mean()
    ratio = (sub / overall).replace([np.inf, -np.inf], np.nan)
    ratio_rows.append({"标签": tag, "样本数": len(sub_df), **ratio})
ratio_df = pd.DataFrame(ratio_rows)

# 写入报告
lines = [
    "# 广告素材数据分析报告（排除极值后）",
    "",
    "在按 **Impressions（展示量）** 的 IQR 方法剔除极值素材后，对剩余素材重新做概览、标签对比与相关性分析。",
    "",
    "---",
    "",
    "## 一、极值排除说明",
    "",
    f"- **方法**：Impressions 的 IQR，超出 [Q1－1.5×IQR, Q3＋1.5×IQR] 的素材视为极值并排除。",
    f"- **排除素材数**：{n_excluded} 条",
    f"- **参与分析素材数**：{len(df_in)} 条",
    "",
]
if n_excluded > 0 and excluded_names:
    lines.append("**被排除的素材（HTML 名称）**：")
    lines.append("")
    for name in excluded_names[:20]:
        lines.append(f"- {name}")
    if len(excluded_names) > 20:
        lines.append(f"- … 共 {len(excluded_names)} 条")
    lines.extend(["", ""])

lines.extend([
    "---",
    "",
    "## 二、数据概览（排除极值后）",
    "",
    "| 项目 | 数值 |",
    "|------|------|",
    f"| 总行数 | {len(df_in)} |",
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
    "---",
    "",
    "## 三、标签表现对比（排除极值后）",
    "",
    "按「目标物品优先，其次点消、拖消」归为单一标签，与**排除极值后的整体均值**对比。",
    "",
    "| 标签 | 样本数 | 展示量比 | 花费比 | 点击量比 | CTR比 | 跳转率比 | 完播率比 | 通关率比 | 停留时长比 | 报错率比 |",
    "|------|--------|----------|--------|----------|------|----------|----------|----------|------------|----------|",
])
for _, r in ratio_df.iterrows():
    tag = r["标签"]
    n = int(r["样本数"])
    def f(x):
        if pd.isna(x): return "-"
        return f"{x:.2f}"
    imp = r.get("Impressions", np.nan)
    spend = r.get("Spend", np.nan)
    cta = r.get("CTA clicked", np.nan)
    ctr = r.get("CTA click rate", np.nan)
    cvr = r.get("Unique redirects rate", np.nan)
    comp = r.get("HTML completion rate", np.nan)
    solve = r.get("Challenge solved rate", np.nan)
    dur = r.get("Average duration", np.nan)
    err = r.get("Runtime error rate", np.nan)
    lines.append(f"| {tag} | {n} | {f(imp)} | {f(spend)} | {f(cta)} | {f(ctr)} | {f(cvr)} | {f(comp)} | {f(solve)} | {f(dur)} | {f(err)} |")

lines.extend([
    "",
    "---",
    "",
    "## 四、相关性分析（排除极值后）",
    "",
    f"完整相关矩阵已导出：`{OUT_PREFIX}_correlation_pearson.csv`、`{OUT_PREFIX}_correlation_spearman.csv`。",
    "",
    "### 4.1 率指标之间强相关 (|Pearson| ≥ 0.5)",
    "",
    "| 指标 A | 指标 B | Pearson | Spearman |",
    "|--------|--------|---------|----------|",
])
for a, b, p, s in rate_pairs[:18]:
    lines.append(f"| {a} | {b} | {p:.3f} | {s:.3f} |")
lines.extend([
    "",
    "### 4.2 标签与指标相关 (|Pearson| ≥ 0.2)",
    "",
    "| 指标 A | 指标 B | Pearson | Spearman |",
    "|--------|--------|---------|----------|",
])
for a, b, p, s in tag_pairs[:20]:
    lines.append(f"| {a} | {b} | {p:.3f} | {s:.3f} |")
lines.extend([
    "",
    "### 4.3 全表最强相关对 (按 |Pearson| 前 12 对)",
    "",
    "| 指标 A | 指标 B | Pearson | Spearman |",
    "|--------|--------|---------|----------|",
])
for a, b, p, s in pairs_sorted[:12]:
    lines.append(f"| {a} | {b} | {p:.3f} | {s:.3f} |")
lines.extend([
    "",
    "---",
    "",
    "## 五、与未排除极值时的对比小结",
    "",
    "- 排除极值后，**整体均值**（如平均 CTR、CVR、完播率）更贴近「大多数素材」的水平，不被少数极高/极低展示素材拉偏。",
    "- **标签对比**的比值是在「排除极值后的整体」基础上计算，各标签相对差异可能有所变化。",
    "- **相关性**在去掉极值后，线性/秩关系更反映主体分布，可对比 `tag_correlation_*.csv` 与 `tag_no_outliers_correlation_*.csv` 查看差异。",
    "",
])

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Excluded {n_excluded} outlier(s) by Impressions IQR. Analyzed {len(df_in)} rows.")
if excluded_names:
    print("Excluded HTML:", excluded_names)
print(f"Output: {OUT_MD}, {OUT_PREFIX}_correlation_pearson.csv, {OUT_PREFIX}_correlation_spearman.csv")
