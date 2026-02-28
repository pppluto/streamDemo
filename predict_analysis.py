# -*- coding: utf-8 -*-
"""
预测分析入门脚本：基于 tag.xlsx Sheet2 做简单回归与二分类预测。

用法：
  python predict_analysis.py

输出：
  - 控制台打印：各任务的交叉验证指标
  - predict_分析结果.md：简要结论与扩展建议
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict, cross_validate, KFold
from sklearn.linear_model import Ridge
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

FILE = "tag.xlsx"
OUT_MD = "predict_分析结果.md"

# 读取与列名对齐（与 analyze_tag.py 一致）
df = pd.read_excel(FILE, sheet_name="Sheet2", engine="openpyxl")
if len(df.columns) >= 5:
    df = df.rename(columns={
        df.columns[2]: "点消",
        df.columns[3]: "拖消",
        df.columns[4]: "目标物品",
    })

# 特征列：尽量用「原因侧」指标，避免用与目标强同源的指标（减少信息泄漏）
# 标签列用 0 填充缺失，便于参与建模
TAG_COLS = ["点消", "拖消", "目标物品"]
FEATURE_COLS = [
    "点消", "拖消", "目标物品",
    "HTML completion rate",
    "Challenge pass 25 rate", "Challenge pass 50 rate", "Challenge pass 75 rate",
    "Average duration",
    "Black view error rate", "Rendering error rate", "Runtime error rate",
]

# 确保存在的列
FEATURE_COLS = [c for c in FEATURE_COLS if c in df.columns]
for c in TAG_COLS:
    if c in df.columns:
        df[c] = df[c].fillna(0)

# 目标变量定义
TARGET_REGRESSION = "Unique redirects rate"   # CVR，连续值
TARGET_BINARY = "Unique redirects rate"        # 二分类：是否高于中位数

def get_xy(target_col, binary=False):
    """构造 X, y，剔除目标缺失的行。"""
    use = [c for c in FEATURE_COLS if c in df.columns]
    X = df[use].copy()
    y = df[target_col].copy()
    if binary:
        med = y.median()
        y = (y > med).astype(int)
    mask = y.notna()
    X, y = X.loc[mask], y.loc[mask]
    # 数值列缺失用中位数填
    for c in X.select_dtypes(include=[np.number]).columns:
        if X[c].isna().any():
            X[c] = X[c].fillna(X[c].median())
    return X, y

def run_regression():
    """回归：预测 CVR（Unique redirects rate）。"""
    if TARGET_REGRESSION not in df.columns:
        return None
    X, y = get_xy(TARGET_REGRESSION, binary=False)
    if len(X) < 10:
        return None
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", Ridge(alpha=1.0)),
    ])
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_validate(pipe, X, y, cv=cv, scoring=["r2", "neg_mean_absolute_error", "neg_root_mean_squared_error"])
    return {
        "n_samples": len(X),
        "r2": scores["test_r2"].mean(),
        "mae": -scores["test_neg_mean_absolute_error"].mean(),
        "rmse": -scores["test_neg_root_mean_squared_error"].mean(),
    }

def run_classification():
    """二分类：预测 CVR 是否高于中位数。"""
    if TARGET_BINARY not in df.columns:
        return None
    X, y = get_xy(TARGET_BINARY, binary=True)
    if len(X) < 10 or y.nunique() < 2:
        return None
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", LogisticRegression(max_iter=500, random_state=42)),
    ])
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_validate(pipe, X, y, cv=cv, scoring=["accuracy", "f1_weighted", "roc_auc"])
    return {
        "n_samples": len(X),
        "accuracy": scores["test_accuracy"].mean(),
        "f1_weighted": scores["test_f1_weighted"].mean(),
        "roc_auc": scores["test_roc_auc"].mean(),
    }

def main():
    print("Predict (tag.xlsx Sheet2)")
    print("Features:", FEATURE_COLS)
    print()

    reg = run_regression()
    if reg:
        print("[Regression] Target:", TARGET_REGRESSION)
        print(f"  n_samples: {reg['n_samples']}")
        print(f"  R2 (5-fold CV): {reg['r2']:.4f}")
        print(f"  MAE:        {reg['mae']:.6f}")
        print(f"  RMSE:       {reg['rmse']:.6f}")
        print()
    else:
        reg = {}

    clf = run_classification()
    if clf:
        print("[Classification] Target: {} above median?".format(TARGET_BINARY))
        print(f"  n_samples: {clf['n_samples']}")
        print(f"  Accuracy: {clf['accuracy']:.4f}")
        print(f"  F1(w):   {clf['f1_weighted']:.4f}")
        print(f"  ROC AUC: {clf['roc_auc']:.4f}")
        print()
    else:
        clf = {}

    # 写简短结论
    lines = [
        "# 预测分析结果",
        "",
        "基于 **tag.xlsx Sheet2** 的入门级预测分析（5 折交叉验证）。",
        "",
        "## 一、设定",
        "",
        "- **特征**：点消、拖消、目标物品、完播率、挑战通过率(25/50/75)、平均时长、各类报错率。",
        "- **回归目标**：`Unique redirects rate`（跳转转化率 CVR）。",
        "- **分类目标**：CVR 是否高于中位数（高/低转化）。",
        "",
        "## 二、结果摘要",
        "",
    ]
    if reg:
        lines.extend([
            "### 回归（预测 CVR）",
            "",
            f"- 有效样本数：{reg.get('n_samples', '-')}",
            f"- R²：{reg.get('r2', 0):.4f}（越接近 1 拟合越好，样本少时易偏低）",
            f"- MAE：{reg.get('mae', 0):.6f}",
            f"- RMSE：{reg.get('rmse', 0):.6f}",
            "",
        ])
    if clf:
        lines.extend([
            "### 二分类（高/低 CVR）",
            "",
            f"- 有效样本数：{clf.get('n_samples', '-')}",
            f"- Accuracy：{clf.get('accuracy', 0):.4f}",
            f"- F1 (weighted)：{clf.get('f1_weighted', 0):.4f}",
            f"- ROC AUC：{clf.get('roc_auc', 0):.4f}",
            "",
        ])
    lines.extend([
        "## 三、如何继续做预测分析",
        "",
        "1. **换预测目标**：在脚本中修改 `TARGET_REGRESSION` / `TARGET_BINARY`，例如改为 `CTA click rate`、`HTML completion rate`、`Challenge pass 50 rate` 等。",
        "2. **增加/删减特征**：修改 `FEATURE_COLS`，注意避免「用目标或强相关结果当特征」（信息泄漏）。",
        "3. **换模型**：可尝试 `RandomForestRegressor` / `RandomForestClassifier`（样本少时易过拟合，建议用 CV 看泛化）。",
        "4. **样本增多后**：再做特征筛选（如基于相关性或模型 feature_importance）、调参，或划分固定测试集评估。",
        "",
    ])
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Written:", OUT_MD)

if __name__ == "__main__":
    main()
