# utils_stock.py
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Sequence, Optional
from dataclasses import dataclass
from scipy.optimize import minimize

# ---------- 讀檔 / 清理 ----------

def load_prices_csv(path: str, date_col: str="Date") -> pd.DataFrame:
    """
    讀取收盤價CSV（寬表）：第一欄為日期，後面每欄一個資產/股票價格
    - 自動把日期設成索引並排序
    - 自動去除完全空的列/欄
    """
    df = pd.read_csv(path)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    return df

def to_returns(prices: pd.DataFrame, method: str="simple", dropna: bool=True) -> pd.DataFrame:
    """
    將價格轉成報酬率：
    - method="simple": r_t = P_t / P_{t-1} - 1
    - method="log":    r_t = ln(P_t) - ln(P_{t-1})
    """
    if method == "simple":
        ret = prices.pct_change()
    elif method == "log":
        ret = np.log(prices).diff()
    else:
        raise ValueError("method must be 'simple' or 'log'")
    return ret.dropna() if dropna else ret

# ---------- 指標計算 ----------

@dataclass
class RiskStats:
    ann_return: float
    ann_vol: float
    sharpe: float
    cagr: float
    max_drawdown: float
    cvar_95: float

def annualize_mean_vol(returns: pd.DataFrame, periods_per_year: int=252) -> Tuple[pd.Series, pd.Series]:
    mu = returns.mean() * periods_per_year
    vol = returns.std(ddof=0) * np.sqrt(periods_per_year)
    return mu, vol

def sharpe_ratio(returns: pd.DataFrame | pd.Series, rf: float=0.0, periods_per_year: int=252) -> float | pd.Series:
    """
    單資產: Series -> float；多資產: DataFrame -> 每欄一個Sharpe的Series
    rf 為「每期」的無風險利率（若你給年化rf，請除以 periods_per_year）
    """
    if isinstance(returns, pd.Series):
        ex = returns - rf
        return (ex.mean()*periods_per_year) / (ex.std(ddof=0)*np.sqrt(periods_per_year))
    else:
        ex = returns - rf
        mu, vol = annualize_mean_vol(ex, periods_per_year)
        return mu / vol

def cagr_from_prices(prices: pd.Series) -> float:
    years = (prices.index[-1] - prices.index[0]).days / 365.25
    return (prices.iloc[-1] / prices.iloc[0])**(1/years) - 1

def max_drawdown(prices: pd.Series) -> float:
    cummax = prices.cummax()
    drawdown = prices / cummax - 1.0
    return drawdown.min()

def cvar(returns: pd.Series, alpha: float=0.95) -> float:
    """
    以「損失為正」的慣例回傳 CVaR：例如 -0.02 的尾端平均 → 回傳 0.02
    """
    q = returns.quantile(1 - alpha)
    tail = returns[returns <= q]
    return -tail.mean()

def portfolio_stats(weights: np.ndarray, returns: pd.DataFrame, rf: float=0.0, periods_per_year: int=252) -> Dict[str, float]:
    """
    根據權重計算投組年化報酬/波動/Sharpe。
    """
    w = np.asarray(weights)
    port_ret = (returns @ w)
    ann_ret = port_ret.mean()*periods_per_year
    ann_vol = port_ret.std(ddof=0)*np.sqrt(periods_per_year)
    sharpe = (ann_ret - rf) / (ann_vol + 1e-12)
    # 將 returns 累積成等權重組合的「價格」概念以估MDD / CVaR
    port_price = (1 + port_ret).cumprod()
    mdd = max_drawdown(port_price)
    cvar95 = cvar(port_ret, alpha=0.95)
    return {"ann_return": float(ann_ret), "ann_vol": float(ann_vol), "sharpe": float(sharpe),
            "max_drawdown": float(mdd), "cvar_95": float(cvar95)}

# ---------- 最大夏普配置（帶上下限、權重加總=1） ----------

def max_sharpe_weights(
    returns: pd.DataFrame,
    rf: float=0.0,
    bounds: Optional[Sequence[Tuple[float,float]]] = None,
    periods_per_year: int=252,
    x0: Optional[np.ndarray]=None
) -> np.ndarray:
    """
    用 scipy.optimize 最大化 Sharpe：
    - returns: (T x N) 的報酬率
    - rf: 每期無風險利率（年化請自行除以 periods_per_year）
    - bounds: 權重上下限，預設(0,1)
    - 權重會自動加總=1
    """
    n = returns.shape[1]
    if bounds is None:
        bounds = [(0.0, 1.0)] * n
    if x0 is None:
        x0 = np.ones(n) / n

    def neg_sharpe(w):
        s = portfolio_stats(w, returns, rf=rf, periods_per_year=periods_per_year)["sharpe"]
        return -s

    cons = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)
    res = minimize(neg_sharpe, x0=x0, bounds=bounds, constraints=cons, method="SLSQP")
    return res.x

# ---------- 一站式：讀檔→報酬→最優權重→輸出統計 ----------

def quick_max_sharpe_from_csv(
    path: str, date_col: str="Date", method: str="simple",
    rf_annual: float=0.0, periods_per_year: int=252,
    bounds: Optional[Sequence[Tuple[float,float]]] = None
) -> Dict[str, Any]:
    prices = load_prices_csv(path, date_col=date_col)
    rets = to_returns(prices, method=method, dropna=True)
    rf_per_period = rf_annual / periods_per_year
    w = max_sharpe_weights(rets, rf=rf_per_period, bounds=bounds, periods_per_year=periods_per_year)
    stats = portfolio_stats(w, rets, rf=rf_per_period, periods_per_year=periods_per_year)
    return {"weights": pd.Series(w, index=rets.columns), "stats": stats}
