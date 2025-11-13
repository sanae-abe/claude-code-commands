# Data Science Development

## 📋 クイックスタート

```bash
# Jupyter環境起動（99%使用）
jupyter lab              # Jupyter Lab起動（推奨）
jupyter notebook         # Jupyter Notebook起動

# Python環境（95%使用）
python script.py         # スクリプト実行
ipython                  # 対話型Python

# 実験管理（85%使用）
mlflow ui                # MLflow UI起動
dvc pull                 # データバージョン管理
wandb login              # Weights & Biases連携
```

## 🎯 品質基準

### コード品質
- **Type Hints**: 関数シグネチャに型ヒント
- **Docstrings**: 関数・クラスのドキュメント
- **Linter**: flake8、pylintで0エラー
- **Formatter**: blackで統一フォーマット

### 再現性
- **環境管理**: conda/venv + requirements.txt
- **乱数固定**: random_state/seedの明示的設定
- **データバージョニング**: DVC使用
- **実験管理**: MLflow、Weights & Biases

### ドキュメント
- **README**: 環境構築手順、実行方法
- **Notebook**: マークダウンセルで説明
- **結果記録**: 実験結果、パラメータ、メトリクス

## 🔒 データセキュリティ

### 個人情報保護
- **匿名化**: 個人識別情報の削除・マスク
- **アクセス制御**: データへのアクセス権限管理
- **暗号化**: 機密データの暗号化保存

### データ管理
```python
# 機密データの安全な読み込み
import os
from dotenv import load_dotenv

load_dotenv()  # .envから読み込み
DB_PASSWORD = os.getenv('DB_PASSWORD')  # 環境変数使用

# ❌ ハードコード禁止
# DB_PASSWORD = "secret123"
```

## 📊 データ処理

### パフォーマンス最適化
- **pandas**: データフレーム操作、vectorization活用
- **numpy**: 数値計算、行列演算
- **dask**: 大規模データ並列処理
- **polars**: 高速DataFrame（Rust実装）

### メモリ管理
```python
import pandas as pd

# メモリ効率的な読み込み
df = pd.read_csv('large_file.csv',
    dtype={'col1': 'int32'},  # 型指定で削減
    usecols=['col1', 'col2'],  # 必要列のみ
    chunksize=10000  # チャンク読み込み
)

# メモリ使用量確認
print(df.memory_usage(deep=True))
```

## 💡 実践例

### ケース1: データ前処理パイプライン
```python
# 状況: 雑然としたデータ前処理コード

# ❌ 読みにくい実装
df = pd.read_csv('data.csv')
df = df[df['age'] > 0]
df['age_group'] = pd.cut(df['age'], bins=[0, 20, 40, 60, 100])
df = df.dropna()
df = pd.get_dummies(df, columns=['category'])

# ✅ パイプライン化
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

# 前処理パイプライン定義
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), ['age', 'income']),
    ('cat', OneHotEncoder(), ['category'])
])

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', RandomForestClassifier())
])

# 実行
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)

# 結果: 再現性向上、コード可読性向上
```

### ケース2: 実験管理（MLflow）
```python
# 状況: 実験結果が散逸、再現困難

import mlflow
import mlflow.sklearn

# ✅ MLflowで実験管理
with mlflow.start_run():
    # パラメータ記録
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)

    # モデル学習
    model = RandomForestClassifier(n_estimators=100, max_depth=10)
    model.fit(X_train, y_train)

    # メトリクス記録
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # モデル保存
    mlflow.sklearn.log_model(model, "model")

    # アーティファクト保存（図表等）
    plt.figure()
    plot_confusion_matrix(model, X_test, y_test)
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")

# 結果: 実験の完全な再現性、比較容易
# MLflow UI で全実験を比較可能
```

### ケース3: 大規模データ処理（Dask）
```python
# 状況: pandas で100GBデータ処理がメモリ不足

import dask.dataframe as dd

# ❌ pandas（メモリ不足）
# df = pd.read_csv('100gb_file.csv')  # MemoryError

# ✅ Dask（並列処理）
df = dd.read_csv('100gb_file.csv')

# pandas と同じ API
result = df.groupby('category')['value'].mean().compute()

# 並列処理で高速化
from dask.distributed import Client
client = Client(n_workers=4)  # 4並列

# 結果: 100GBデータを処理可能、4倍高速化
```

### よくあるパターン

#### データ前処理
- **欠損値**: fillna、dropna、補完（平均値、中央値、KNN）
- **外れ値**: IQR法、Z-score、winsorization
- **スケーリング**: StandardScaler、MinMaxScaler、RobustScaler

#### モデル評価
- **分類**: accuracy、precision、recall、F1、ROC-AUC
- **回帰**: MSE、RMSE、MAE、R²
- **交差検証**: k-fold、stratified k-fold、time series split

#### 可視化
- **matplotlib**: 基本プロット
- **seaborn**: 統計的可視化
- **plotly**: インタラクティブ可視化

## 🔧 技術スタック選択ガイド

### Python
- **適用**: 機械学習、データ分析、豊富なライブラリ
- **特徴**: scikit-learn、pandas、numpy、TensorFlow、PyTorch
- **注意点**: パフォーマンス（GIL制限）

### R
- **適用**: 統計分析、アカデミック、可視化重視
- **特徴**: tidyverse、ggplot2、統計パッケージ豊富
- **注意点**: 機械学習ライブラリは Python に劣る

### Julia
- **適用**: 高性能計算、科学技術計算
- **特徴**: Python 並みの書きやすさ、C 並みの速度
- **注意点**: エコシステム成熟度

## 📚 参考リソース

- **pandas公式**: https://pandas.pydata.org/
- **scikit-learn公式**: https://scikit-learn.org/
- **MLflow公式**: https://mlflow.org/
- **Kaggle Learn**: https://www.kaggle.com/learn
