# -*- coding: utf-8 -*-
"""按点消/拖消/目标物品分组，对比关键指标，输出「哪些标签较突出」的结论。"""
import pandas as pd
import numpy as np

df = pd.read_excel("tag.xlsx", sheet_name="Sheet2", engine="openpyxl")
df = df.rename(columns={df.columns[2]: "点消", df.columns[3]: "拖消", df.columns[4]: "目标物品"})
for c in ["点消", "拖消", "目标物品"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

def assign_tag(row):
    if row.get("目标物品") == 1:
        return "目标物品"
    if row.get("点消") == 1:
        return "点消"
    if row.get("拖消") == 1:
        return "拖消"
    return "未标注"

df["_tag"] = df.apply(assign_tag, axis=1)

metrics = [
    "Impressions", "Spend", "CTA clicked", "CTA click rate",
    "Unique redirects rate", "HTML completion rate", "Challenge solved rate",
    "Average duration", "Runtime error rate",
]
metrics = [m for m in metrics if m in df.columns]

overall = df[metrics].mean()
by_tag = df.groupby("_tag")[metrics].agg(["mean", "count"]).round(4)

# 相对整体的比值（仅标签组，不含未标注）
rows = []
for tag in ["点消", "拖消", "目标物品"]:
    if tag not in by_tag.index:
        continue
    sub = df[df["_tag"] == tag][metrics].mean()
    ratio = (sub / overall).replace([np.inf, -np.inf], np.nan)
    n = len(df[df["_tag"] == tag])
    rows.append({"标签": tag, "样本数": n, **ratio})

ratio_df = pd.DataFrame(rows)
ratio_df = ratio_df.set_index("标签")
ratio_df.to_csv("tag_标签对比_相对整体比值.csv", encoding="utf-8-sig")
by_tag.to_csv("tag_标签对比_分组均值.csv", encoding="utf-8-sig")

# 文本结论
lines = [
    "## 标签表现对比：哪些标签较突出",
    "",
    "按「点消=1 / 拖消=1 / 目标物品=1」将每条素材归为单一标签（目标物品优先，其次点消、拖消），与整体均值对比，得到各标签相对整体的比值（>1 表示高于整体，<1 表示低于整体）。",
    "",
    "| 标签 | 样本数 | 展示量比 | 花费比 | 点击量比 | CTR比 | 跳转率比 | 完播率比 | 通关率比 | 停留时长比 | 报错率比 |",
    "|------|--------|----------|--------|----------|------|----------|----------|----------|------------|----------|",
]
for tag in ["点消", "拖消", "目标物品"]:
    if tag not in ratio_df.index:
        continue
    r = ratio_df.loc[tag]
    n = int(ratio_df.loc[tag].get("样本数", 0)) if "样本数" in ratio_df.columns else int(df["_tag"].value_counts().get(tag, 0))
    # 从 by_tag 取 count
    n = len(df[df["_tag"] == tag])
    imp = r.get("Impressions", np.nan)
    spend = r.get("Spend", np.nan)
    cta = r.get("CTA clicked", np.nan)
    ctr = r.get("CTA click rate", np.nan)
    cvr = r.get("Unique redirects rate", np.nan)
    comp = r.get("HTML completion rate", np.nan)
    solve = r.get("Challenge solved rate", np.nan)
    dur = r.get("Average duration", np.nan)
    err = r.get("Runtime error rate", np.nan)
    def f(x):
        if pd.isna(x): return "-"
        return f"{x:.2f}"
    lines.append(f"| {tag} | {n} | {f(imp)} | {f(spend)} | {f(cta)} | {f(ctr)} | {f(cvr)} | {f(comp)} | {f(solve)} | {f(dur)} | {f(err)} |")

lines.extend([
    "",
    "**结论摘要**：",
    "",
])

# 自动写结论
conclusions = []
for tag in ["点消", "拖消", "目标物品"]:
    if tag not in ratio_df.index:
        continue
    r = ratio_df.loc[tag]
    n = len(df[df["_tag"] == tag])
    pts = []
    if r.get("Impressions", 0) > 1.5:
        pts.append("展示量/花费/点击量明显高于整体")
    elif r.get("Impressions", 1) < 0.5:
        pts.append("展示量/花费/点击量低于整体")
    if r.get("CTA click rate", 1) > 1.2:
        pts.append("CTR 高于整体")
    elif r.get("CTA click rate", 1) < 0.85:
        pts.append("CTR 低于整体")
    if r.get("Challenge solved rate", 1) > 1.2:
        pts.append("通关率高于整体")
    elif r.get("Challenge solved rate", 1) < 0.7:
        pts.append("通关率低于整体")
    if r.get("HTML completion rate", 1) < 0.6:
        pts.append("完播率明显低于整体")
    if pts:
        conclusions.append(f"- **{tag}**（n={n}）：" + "；".join(pts) + "。")

if conclusions:
    lines.extend(conclusions)
else:
    lines.append("- 各标签样本量较小，差异以比值表为准，可结合业务判断。")

lines.append("")
with open("tag_标签突出结论.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Done: tag_标签对比_相对整体比值.csv, tag_标签对比_分组均值.csv, tag_标签突出结论.md")
print(ratio_df.to_string())
