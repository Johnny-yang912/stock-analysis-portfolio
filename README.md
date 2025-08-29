# stock-analysis-portfolio
## 📈 股市分析（Python）

## 🧾 專案簡介  
本專案透過 Python 進行股市資料分析，涵蓋資料擷取、清理與風險指標計算（Sharpe Ratio、Sortino Ratio、Max Drawdown、CVaR），並進一步嘗試簡單的資產配置分析。
整體流程以 Jupyter Notebook 為核心，重點在於展示金融資料分析的完整思維與成果，同時亦提供簡易化的分析工具，雖非完整封裝，但能展現團隊合作與模組化開發的思維。

本專案包含：

- **Notebook**：完整的分析過程與可視化
- **工具包 (`utils_stock.py`)**：基本版模組化工具，方便團隊快速重現與擴展分析流程

## 📊 報告展示（PDF）  
👉 [點我查看完整報告 PDF](股市資料分析pdf.pdf)  
👉 [查看 Jupyter Notebook](股市分析.ipynb) 


## 📁 檔案內容  

| 檔名                  | 說明                                   |
|-----------------------|--------------------------------------|
| 股市分析.ipynb        | 主要 Notebook，完整分析流程            |
| 股市資料分析pdf.pdf    | 總結報告 PDF                          |
| README.md             | 專案說明文件                          |
| LICENSE               | 授權條款                              |
| .gitignore            | Git 忽略設定                          |

## 🔍 分析內容  
本分析涵蓋：  
•	股票資料下載與整理  
•	報酬率、波動度等基本指標  
•	風險衡量：Sharpe、Sortino、Max Drawdown、CVaR  
•	簡單資產配置示範（最大夏普比率）  

## 📈 成果與圖表  
•	🎯 風險與報酬率比較  
•	📊 資產配置下的權重分布  
•	📄 完整結論請見報告 PDF  

## 💡 專案重點與洞察  
•	風險指標能提供投資決策的輔助依據  
•	不同衡量方式（Sharpe vs CVaR）會導致配置差異  
•	限制單一資產比重有助於降低極端風險  


## 🧰 工具包（utils_stock.py）

提供常用的風險與配置工具：報酬、Sharpe、MDD、CVaR、**最大夏普比率資產配置**。

### 安裝需求
```bash
pip install -r requirements.txt
```
### 快速上手：一行求最大夏普比率配置
```
from utils_stock import quick_max_sharpe_from_csv

res = quick_max_sharpe_from_csv(
    "prices.csv",          # 寬表價格CSV，第一欄Date，其餘為各資產
    rf_annual=0.01         # 年化無風險利率（例：1%）
)
print(res["weights"])      # 各資產權重
print(res["stats"])        # {'ann_return':..., 'ann_vol':..., 'sharpe':..., 'max_drawdown':..., 'cvar_95':...}
```

### 進階：自訂上下限（例如每檔 0%~60%）
```
from utils_stock import load_prices_csv, to_returns, max_sharpe_weights, portfolio_stats

prices = load_prices_csv("prices.csv", date_col="Date")
rets = to_returns(prices, method="simple")
bounds = [(0.0, 0.6)] * rets.shape[1]     # 每檔資產上下限
w = max_sharpe_weights(rets, rf=0.01/252, bounds=bounds)  # rf 換成每期利率
stats = portfolio_stats(w, rets, rf=0.01/252)

```
### 附件
🔧 工具包 [./utils_stock.py](./utils_stock.py)  
🔎 使用範例 [./test.ipynb](./test.ipynb)

________________________________________  
## 🙋‍♂️ 作者說明  
本作品為個人練習與求職作品，資料來源自 Yahoo Finance，目的在於展示數據分析與金融應用能力。  
⚠️ 警告：本專案資料與分析結果僅供學習參考，切勿用於任何實務投資決策。  
