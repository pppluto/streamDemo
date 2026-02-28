# -*- coding: utf-8 -*-
"""相关性分析：从 sksx.xlsx 计算并找出强相关指标对"""
import pandas as pd
import numpy as np

df = pd.read_excel('sksx.xlsx', engine='openpyxl')
numeric = df.select_dtypes(include=[np.number])
numeric = numeric.dropna(axis=1, how='all')
numeric = numeric.loc[:, numeric.nunique() > 1]

corr_pearson = numeric.corr(method='pearson')
corr_spearman = numeric.corr(method='spearman')

# 保存完整相关矩阵，便于后续查看
corr_pearson.to_csv('correlation_pearson.csv', encoding='utf-8-sig')
corr_spearman.to_csv('correlation_spearman.csv', encoding='utf-8-sig')

n = len(corr_pearson)
pairs = []
for i in range(n):
    for j in range(i + 1, n):
        a, b = corr_pearson.columns[i], corr_pearson.columns[j]
        p_val = corr_pearson.iloc[i, j]
        s_val = corr_spearman.iloc[i, j]
        pairs.append((a, b, float(p_val), float(s_val)))

pairs_sorted = sorted(pairs, key=lambda x: abs(x[2]), reverse=True)

# 只保留「率」与「率」或「率」与其它有业务解释的配对，排除纯计数间的规模相关
rate_cols = [c for c in numeric.columns if 'rate' in c.lower()]
def is_rate_pair(a, b):
    return (a in rate_cols) or (b in rate_cols)
def is_interesting(a, b, p):
    # 两个都是 rate：业务上最值得看
    if a in rate_cols and b in rate_cols and abs(p) >= 0.5:
        return True
    # 一个 rate 一个非 rate（如 Average duration）：也有解释意义
    if is_rate_pair(a, b) and 0.4 <= abs(p) < 0.95:
        return True
    return False

interesting = [(a, b, p, s) for a, b, p, s in pairs_sorted if is_interesting(a, b, p)]

print("=== 业务相关：率指标之间 / 率与关键指标 (Pearson 绝对值排序) ===")
print(f"{'Col A':<38} {'Col B':<38} {'Pearson':>10} {'Spearman':>10}")
print("-" * 98)
for a, b, p, s in interesting[:35]:
    print(f"{a[:37]:<38} {b[:37]:<38} {p:>10.3f} {s:>10.3f}")

# 强相关阈值
high = [(a, b, p, s) for a, b, p, s in pairs_sorted if abs(p) >= 0.7]
print("\n=== |Pearson| >= 0.7 的强相关对 (前 45 对) ===")
for a, b, p, s in high[:45]:
    print(f"  {a}  <->  {b}   P={p:.3f}  S={s:.3f}")

# 中等相关 0.5 ~ 0.7
mid = [(a, b, p, s) for a, b, p, s in pairs_sorted if 0.5 <= abs(p) < 0.7]
print("\n=== 0.5 <= |Pearson| < 0.7 的中等相关对 (前20对) ===")
for a, b, p, s in mid[:20]:
    print(f"  {a}  <->  {b}   P={p:.3f}  S={s:.3f}")
