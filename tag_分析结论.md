# tag.xlsx 数据分析结论

基于 **tag.xlsx**：37 行、44 列。数值列参与相关性的共 39 列。

---

## 一、数据概览

| 项目 | 数值 |
|------|------|
| 总行数 | 37 |
| 唯一素材数 (HTML) | 37 |
| 总展示量 (Impressions) | 3,074,333 |
| 总花费 (Spend) | $67,017.02 |
| 总点击 (CTA clicked) | 495,642 |
| 平均点击率 (CTR) | 13.52% |
| 平均跳转转化率 (CVR) | 12.92% |
| 平均互动率 (IVR) | 34.82% |
| 平均完播率 | 188.38% |
| 展示量 > 1000 的行数 | 29 |
| 展示量 > 10000 的行数 | 9 |
| CTA clicked > 0 的行数 | 33 |
| 有明确游戏结果 (solved>50 & failed>50) | 15 |
| 限时自由玩 (solved=0 & failed=0) | 3 |

| **点消** 非空数 / 均值 / 标准差 | 13 / 0.462 / 0.519 |
| **拖消** 非空数 / 均值 / 标准差 | 13 / 0.538 / 0.519 |
| **目标物品** 非空数 / 均值 / 标准差 | 13 / 0.308 / 0.480 |

---

## 二、标签表现对比：哪些标签较突出

按「点消=1 / 拖消=1 / 目标物品=1」将每条素材归为单一标签（目标物品优先，其次点消、拖消），与整体均值对比，得到各标签相对整体的比值（>1 表示高于整体，<1 表示低于整体）。数据来源：`tag.xlsx` Sheet2，运行 `python tag_label_compare.py` 可刷新下表。

| 标签     | 样本数 | 展示量比 | 花费比 | 点击量比 | CTR比 | 跳转率比 | 完播率比 | 通关率比 | 停留时长比 | 报错率比 |
|----------|--------|----------|--------|----------|------|----------|----------|----------|------------|----------|
| 点消     | 3      | 0.16     | 0.18   | 0.20     | 1.34 | 1.39     | 0.99     | 0.57     | 0.91       | 1.15     |
| 拖消     | 6      | 0.42     | 0.51   | 0.21     | 0.99 | 0.93     | 0.39     | 0.96     | 0.93       | 0.76     |
| 目标物品 | 4      | 7.35     | 7.28   | 7.61     | 0.80 | 0.83     | 1.06     | 1.51     | 0.91       | 0.89     |

**结论摘要**：

- **目标物品**（n=4）：**最突出**。展示量、花费、点击量约为整体的 **7 倍以上**，说明该标签下的素材曝光与消耗明显更大；通关率约为整体的 1.5 倍，完播率略高于整体，报错率略低。
- **点消**（n=3）：展示量/花费/点击量低于整体；**CTR、跳转率高于整体**（约 1.3～1.4 倍），但通关率偏低（约 0.57），报错率略高。
- **拖消**（n=6）：展示量/花费低于整体；**完播率明显低于整体**（约 0.39），其余率指标接近整体。

---

## 三、标签列：点消、拖消、目标物品（与指标的相关）

点消、拖消、目标物品是对**素材打的分类标签**（如 0/1 或类别），不是连续型指标。与指标做相关时，相关系数表示「带该标签的素材与某指标高低的关联」（类似分组差异），适合看哪类标签的素材更偏某指标；若只关心指标与指标之间的相关，分析时可排除这三列。

以下为这三列与其它数值指标的相关系数（|Pearson| ≥ 0.2），便于观察标签与消耗、转化、游戏行为的关系。

| 指标 A | 指标 B | Pearson | Spearman |
|--------|--------|---------|----------|
| 点消 | 拖消 | -1.000 | -1.000 |
| 拖消 | HTML completion rate | -0.728 | -0.701 |
| 点消 | HTML completion rate | 0.728 | 0.701 |
| 目标物品 | Challenge pass 50 rate | 0.643 | 0.624 |
| 目标物品 | Challenge pass 75 rate | 0.632 | 0.535 |
| 目标物品 | Challenge pass 25 rate | 0.623 | 0.579 |
| 目标物品 | Runtime error | 0.556 | 0.356 |
| 目标物品 | Black view error | 0.542 | 0.401 |
| 点消 | Black view error rate | 0.536 | 0.537 |
| 拖消 | Black view error rate | -0.536 | -0.537 |
| 目标物品 | HTML completion rate | 0.521 | 0.535 |
| 目标物品 | Rendering error | 0.495 | 0.344 |
| 目标物品 | Spend | 0.494 | 0.445 |
| 目标物品 | Total interactions | 0.488 | 0.401 |
| 目标物品 | Impressions | 0.487 | 0.356 |
| 目标物品 | HTML completed | 0.487 | 0.401 |
| 目标物品 | Endcard shown | 0.486 | 0.356 |
| 目标物品 | Unique redirects | 0.485 | 0.045 |
| 目标物品 | Redirect count | 0.485 | 0.045 |
| 目标物品 | CTA clicked | 0.485 | 0.000 |
| 目标物品 | HTML loaded | 0.479 | 0.312 |
| 目标物品 | HTML loading | 0.478 | 0.312 |
| 目标物品 | HTML displayed | 0.477 | 0.312 |
| 目标物品 | Unique interactions | 0.475 | 0.312 |
| 目标物品 | Unique interactions rate | 0.472 | 0.445 |

---

## 四、相关性分析（全表）

完整相关矩阵已导出：`tag_correlation_pearson.csv`、`tag_correlation_spearman.csv`。

### 率指标之间强相关 (|Pearson| ≥ 0.5)

| 指标 A | 指标 B | Pearson | Spearman |
|--------|--------|---------|----------|
| Unique redirects rate | Redirect rate | 1.000 | 1.000 |
| Unique redirects rate | CTA click rate | 0.996 | 0.995 |
| CTA click rate | Redirect rate | 0.996 | 0.995 |
| Black view error rate | Runtime error rate | 0.951 | 0.723 |
| Challenge pass 50 rate | Challenge pass 75 rate | 0.943 | 0.930 |
| Challenge pass 25 rate | Challenge pass 50 rate | 0.928 | 0.939 |
| Challenge pass 25 rate | Challenge pass 75 rate | 0.765 | 0.800 |
| Challenge failed rate | Challenge pass 25 rate | 0.742 | 0.318 |
| HTML completion rate | Challenge pass 50 rate | 0.651 | 0.584 |
| Challenge failed rate | Challenge pass 50 rate | 0.644 | 0.144 |
| HTML completion rate | Challenge pass 25 rate | 0.643 | 0.463 |
| HTML completion rate | Challenge pass 75 rate | 0.600 | 0.585 |
| Unique interactions rate | HTML completion rate | 0.548 | 0.444 |

### 全表最强相关对 (按 |Pearson| 前 15 对)

| 指标 A | 指标 B | Pearson | Spearman |
|--------|--------|---------|----------|
| 点消 | 拖消 | -1.000 | -1.000 |
| Unique redirects | Redirect count | 1.000 | 1.000 |
| HTML loading | HTML loaded | 1.000 | 0.999 |
| Challenge pass 50 | Challenge pass 75 | 1.000 | 0.982 |
| Challenge pass 25 | Challenge pass 50 | 1.000 | 0.983 |
| Unique redirects rate | Redirect rate | 1.000 | 1.000 |
| Unique redirects | CTA clicked | 1.000 | 0.999 |
| CTA clicked | Redirect count | 1.000 | 0.998 |
| HTML loading | HTML displayed | 1.000 | 0.980 |
| Challenge pass 25 | Challenge pass 75 | 1.000 | 0.949 |
| HTML loaded | HTML displayed | 1.000 | 0.983 |
| Unique interactions | HTML displayed | 1.000 | 0.966 |
| Unique interactions | HTML loading | 1.000 | 0.952 |
| Unique interactions | HTML loaded | 1.000 | 0.955 |
| HTML completed | Endcard shown | 1.000 | 0.631 |

---

## 五、与 sksx 的对比说明

若需与 sksx.xlsx 对比，可在 Streamlit 侧栏切换「数据表」分别查看；相关性结论结构一致，数值会随 tag.xlsx 数据更新而变化。
