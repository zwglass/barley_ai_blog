import os
from pathlib import Path

# === 根目录名 ===
# root = Path("arena-qlib-finrl")
root = Path(__file__).parent.parent

# === 目录结构 ===
dirs = [
    "data/raw",
    "data/features",
    "conf",
    "src/agents",
    "reports",
    "logs",
]

# === 要写入的文件内容模板 ===
files_content = {
    "README.md": """# Arena Qlib + FinRL + DeepSeek
多智能体虚拟交易竞赛平台 (Qlib + FinRL + DeepSeek API)
""",
    "requirements.txt": """numpy
pandas
scipy
matplotlib
tqdm
pyyaml
loguru
pytz
ta
yfinance
pyqlib
finrl
stable-baselines3==2.3.2
torch
empyrical-reloaded>=0.5.9
plotly
seaborn
streamlit
openai
""",
    "conf/config.yaml": """symbols_file: conf/symbols_us.txt

data:
  start: "2016-01-01"
  end:   "2025-01-01"
  freq: "1D"
  features: [close, volume, return_1d, ma_5, ma_10, ma_20, volatility_10]

split:
  train: ["2016-01-01", "2019-12-31"]
  valid: ["2020-01-01", "2021-12-31"]
  test:  ["2022-01-01", "2024-12-31"]

broker:
  init_cash: 1000000
  fee_bps: 3
  slippage_bps: 2
  max_position_pct: 0.2

arena:
  agents:
    - name: PPO
      path: artifacts/ppo
      train_steps: 400000
    - name: DeepSeek
      model: deepseek-chat

seed: 42
""",
    "conf/symbols_us.txt": """SPY
AAPL
MSFT
NVDA
GOOGL
AMZN
META
TSLA
""",
    "conf/.env": """# DeepSeek API Key, URL
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=
""",
    "run.sh": """#!/usr/bin/env bash
set -e
echo "=== 初始化数据 ==="
python -m src.qlib_init --config conf/config.yaml

echo "=== 训练 PPO 模型 ==="
python -m src.agents.agent_ppo --config conf/config.yaml --train

echo "=== DeepSeek 对抗 ==="
python -m src.arena --config conf/config.yaml

echo "=== 生成评估报告 ==="
python -m src.evaluate --run_dir latest
python -m src.leaderboard --root_dir reports
""",
    "src/qlib_init.py": """# 初始化 Qlib 数据
def main():
    print("✅ 初始化 Qlib 数据（示例逻辑）")

if __name__ == "__main__":
    main()
""",
    "src/market_feed.py": """# Qlib → FinRL 数据桥接
class MarketFeed:
    def __init__(self):
        pass

    def reset(self, start_date, end_date):
        pass

    def step(self):
        pass
""",
    "src/env_shared.py": """# 虚拟券商/撮合引擎
class VirtualBroker:
    def __init__(self, init_cash=1_000_000):
        self.init_cash = init_cash

    def execute(self, actions_dict):
        # 模拟撮合
        pass
""",
    "src/arena.py": """# 对抗主循环
from agents.agent_ppo import PPOAgent
from agents.agent_deepseek import DeepSeekAgent
from env_shared import VirtualBroker

def main():
    print("🏁 启动对抗赛：PPO vs DeepSeek")
    broker = VirtualBroker()
    ppo = PPOAgent()
    deepseek = DeepSeekAgent()
    # 示例流程
    obs = {"AAPL": {"close": 180}}
    acts = {
        "ppo": ppo.act(obs),
        "deepseek": deepseek.act(obs),
    }
    broker.execute(acts)
    print("✅ 对抗结束")

if __name__ == "__main__":
    main()
""",
    "src/evaluate.py": """# 评估模块
def main():
    print("📊 计算收益指标、绘制曲线")

if __name__ == "__main__":
    main()
""",
    "src/leaderboard.py": """# 榜单生成
def main():
    print("🏆 汇总对抗结果生成榜单")

if __name__ == "__main__":
    main()
""",
    "src/utils.py": """# 通用工具函数
import os, json, datetime
""",
    "src/agents/__init__.py": "",
    "src/agents/agent_ppo.py": """# PPO 智能体
class PPOAgent:
    def __init__(self):
        pass

    def act(self, obs):
        print("PPO 根据观测执行操作")
        return {k: "HOLD" for k in obs.keys()}
""",
    "src/agents/agent_sac.py": """# SAC 智能体
class SACAgent:
    def __init__(self):
        pass

    def act(self, obs):
        return {k: "HOLD" for k in obs.keys()}
""",
    "src/agents/agent_rule.py": """# 简单规则策略（动量型）
class RuleAgent:
    def __init__(self):
        pass

    def act(self, obs):
        return {k: "BUY" for k in obs.keys()}
""",
    "src/agents/agent_deepseek.py": """# DeepSeek 智能体 (API 调用)
""",
}


class ComputePathContent:
    """
    self.cls_compute = ComputePathContent()        #计算内容和路径
    """
    def _compute_content(self, cls_self, def_name):
        # 计算内容
        if hasattr(cls_self, def_name):
            current_attr = getattr(cls_self, def_name)
            return current_attr()
        else:
            return None
        
    def _compute_file_path(self, project_path, def_name, dir_names=None):
        # 计算路径
        if dir_names is not None:
            src_file_path = project_path
            for dir_name in dir_names:
                src_file_path = src_file_path / dir_name
            src_file_path = src_file_path / f'{def_name}.py'
        else:
            src_file_path = project_path / f'{def_name}.py'
        if not src_file_path.parent.is_dir():
            src_file_path.parent.mkdir(parents=True, exist_ok=True)
        return str(src_file_path)
    
    def _write_file(self, file_path, content):
        # 写入文件
        with open(file=file_path, mode='w', encoding='utf-8') as f:
            f.writelines(content)

class SrcFilesContent:
    """文件内容"""
    def __init__(self):
        self.cls_compute = ComputePathContent()        #计算内容和路径
        self.file_names = ['market_feed', 'qlib_init', 'env_shared', 'arena', 'evaluate', 'web_dashboard_utils', ]
        self.project_path = None

    def main_write_files(self, project_path:Path):
        # 文件路径和内容
        self.project_path = project_path
        generated_files_paths = []
        for fn in self.file_names:
            file_path = self.cls_compute._compute_file_path(self.project_path, fn, dir_names=('src', ))
            content = self.cls_compute._compute_content(self, fn)
            self.cls_compute._write_file(file_path, content)    # 保存文件
            generated_files_paths.append(file_path)
        return generated_files_paths

    def market_feed(self):
        # src/market_feed.py —— 市场数据统一接口（真实版）
        lines = """\"\"\"
src/market_feed.py
--------------------------------
功能：
1. 加载 qlib_init 生成的特征数据；
2. 提供 reset(start, end)、step()、get_obs() 等接口；
3. 每次 step() 返回一个“当前时刻的市场快照”；
4. 支持训练、验证、测试/对抗阶段使用同一接口。
\"\"\"

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger


class MarketFeed:
    def __init__(self, data_dir="data/features", symbols_file="conf/symbols_us.txt"):
        self.data_dir = Path(data_dir)
        self.symbols = self._load_symbols(symbols_file)
        self.data = {}       # {symbol: DataFrame}
        self.dates = None
        self.idx = 0

    def _load_symbols(self, file):
        with open(file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def load_data(self):
        \"\"\"加载所有股票数据\"\"\"
        for sym in self.symbols:
            fp = self.data_dir / f"{sym}.csv"
            if not fp.exists():
                logger.warning(f"⚠️ 未找到 {fp}, 跳过")
                continue
            df = pd.read_csv(fp, parse_dates=["Date"], index_col="Date")
            self.data[sym] = df
        if not self.data:
            raise RuntimeError("❌ 未找到任何数据，请先运行 qlib_init.py")

        # 对齐日期
        all_dates = sorted(
            set().union(*(df.index for df in self.data.values()))
        )
        self.dates = pd.to_datetime(all_dates)
        logger.info(f"📅 市场日期范围: {self.dates[0].date()} ~ {self.dates[-1].date()}")

    def reset(self, start_date=None, end_date=None):
        \"\"\"重置数据窗口\"\"\"
        if self.dates is None:
            self.load_data()

        if start_date is not None:
            mask = (self.dates >= pd.to_datetime(start_date)) & (self.dates <= pd.to_datetime(end_date))
            self.active_dates = self.dates[mask]
        else:
            self.active_dates = self.dates

        self.idx = 0
        logger.info(f"🔁 重置市场时间窗口: {self.active_dates[0].date()} - {self.active_dates[-1].date()}")

    def step(self):
        \"\"\"推进一个时间步\"\"\"
        if self.idx >= len(self.active_dates):
            return None, True

        date = self.active_dates[self.idx]
        self.idx += 1
        obs = self.get_obs(date)
        done = self.idx >= len(self.active_dates)
        return obs, done

    def get_obs(self, date):
        \"\"\"获取某天的所有股票行情与特征\"\"\"
        snapshot = {}
        for sym, df in self.data.items():
            if date in df.index:
                row = df.loc[date]
                snapshot[sym] = {
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "return_1d": float(row["return_1d"]),
                    "ma_5": float(row["ma_5"]),
                    "ma_10": float(row["ma_10"]),
                    "ma_20": float(row["ma_20"]),
                    "volatility_10": float(row["volatility_10"]),
                }
        return snapshot


if __name__ == \"__main__\":
    mf = MarketFeed()
    mf.reset("2022-01-01", "2023-01-01")
    for i in range(3):
        obs, done = mf.step()
        print(f"Step {i}: {list(obs.keys())[:3]} ...")
        if done:
            break
"""
        return lines

    def qlib_init(self):
        # src/qlib_init.py —— 数据拉取与特征生成（真实版）
        lines = """\"\"\"
src/qlib_init.py
--------------------------------
功能：
1. 从 conf/symbols_us.txt 读取股票代码；
2. 使用 yfinance 抓取历史数据；
3. 计算常用特征 (收益率、移动均线、波动率等)；
4. 保存到 data/features 目录（按日期索引的 CSV）。
\"\"\"

import os
import sys
import yaml
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from loguru import logger


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"为每个股票计算基础特征\"\"\"
    df["return_1d"] = df["close"].pct_change()
    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_10"] = df["close"].rolling(10).mean()
    df["ma_20"] = df["close"].rolling(20).mean()
    df["volatility_10"] = df["return_1d"].rolling(10).std()
    return df.dropna()


def load_symbols(symbols_file: Path):
    with open(symbols_file, "r", encoding="utf-8") as f:
        syms = [line.strip() for line in f if line.strip()]
    return syms


def fetch_data(symbols, start, end, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for sym in symbols:
        logger.info(f\"📈 下载 {sym} 数据中 ...\")
        try:
            data = yf.download(sym, start=start, end=end, progress=False, group_by=\"column\")
        except Exception as e:
            logger.warning(f\"⚠️ {sym} 下载失败: {e}\")
            continue

        if data.empty:
            logger.warning(f\"⚠️ {sym} 无数据，跳过\")
            continue

        # 🧩 扁平化列名（关键修复）
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        # 统一列名
        df = data.rename(columns={
            \"Open\": \"open\",
            \"High\": \"high\",
            \"Low\": \"low\",
            \"Close\": \"close\",
            \"Volume\": \"volume\",
        })[[\"open\", \"high\", \"low\", \"close\", \"volume\"]]

        # 去除时区
        df.index = df.index.tz_localize(None)

        # 补齐交易日
        df = df.asfreq("B")
        df.fillna(method=\"ffill\", inplace=True)

        # 计算特征
        df = compute_features(df)

        # 保存
        df.to_csv(out_dir / f\"{sym}.csv\", index_label=\"Date\", float_format=\"%.6f\")
        logger.info(f\"✅ 已保存: {out_dir / f\'{sym}.csv\'}\")


def main():
    # === 解析配置 ===
    cfg_file = Path("conf/config.yaml")
    if not cfg_file.exists():
        print("❌ 找不到配置文件 conf/config.yaml")
        sys.exit(1)

    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    symbols_file = Path(cfg["symbols_file"])
    symbols = load_symbols(symbols_file)

    start = cfg["data"]["start"]
    end = cfg["data"]["end"]
    out_dir = Path("data/features")

    # === 日志 ===
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/qlib_init.log", rotation="500 KB")

    logger.info("🚀 开始数据拉取与特征计算 ...")
    fetch_data(symbols, start, end, out_dir)
    logger.info("🏁 数据准备完毕！")


if __name__ == \"__main__\":
    main()
"""
        return lines
    
    def env_shared(self):
        # src/env_shared.py 虚拟券商 / 统一撮合引擎
        lines = """\"\"\"
src/env_shared.py
--------------------------------
虚拟券商 / 统一撮合引擎：
- 维护每个选手的账户（现金、持仓、净值序列）
- 在同一时刻收集所有选手的订单 → 统一撮合
- 支持两类指令：字符串(BUY/SELL/HOLD) 或 数值目标权重(0~1)
- 费用 & 滑点 & 单票权重上限 来自配置
\"\"\"

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from pathlib import Path
from loguru import logger
import pandas as pd
import numpy as np


@dataclass
class Portfolio:
    cash: float
    positions: Dict[str, float] = field(default_factory=dict)   # symbol -> shares
    nav_history: List[Tuple[pd.Timestamp, float]] = field(default_factory=list)


class VirtualBroker:
    def __init__(
        self,
        symbols: List[str],
        init_cash: float = 1_000_000.0,
        fee_bps: float = 3.0,
        slippage_bps: float = 2.0,
        max_position_pct: float = 0.2,
        default_buy_weight: float = 0.1,
    ):
        \"\"\"
        :param symbols: 交易标的列表
        :param init_cash: 初始资金
        :param fee_bps: 单边费率（基点）
        :param slippage_bps: 滑点（基点）
        :param max_position_pct: 单票最大权重
        :param default_buy_weight: 对于 BUY 指令，默认目标权重
        \"\"\"
        self.symbols = list(symbols)
        self.fee = fee_bps / 1e4
        self.slip = slippage_bps / 1e4
        self.max_w = max_position_pct
        self.default_buy_w = min(default_buy_weight, self.max_w)

        self.accounts: Dict[str, Portfolio] = {}  # agent_name -> Portfolio
        self.trade_log_cols = [
            "date", "agent", "symbol", "side", "price_exec",
            "shares", "cash_after", "position_after_value"
        ]
        self._trades: List[dict] = []

    # ---------- 账户 ----------
    def register_agent(self, name: str, init_cash: float):
        self.accounts[name] = Portfolio(cash=init_cash, positions={})
        logger.info(f"👤 注册账户: {name}, 初始现金={init_cash:,.2f}")

    def get_agent_names(self):
        return list(self.accounts.keys())

    # ---------- 估值 ----------
    def _portfolio_value(self, pf: Portfolio, prices: Dict[str, float]) -> float:
        pos_val = 0.0
        for sym, sh in pf.positions.items():
            px = prices.get(sym)
            if px is not None:
                pos_val += sh * px
        return pf.cash + pos_val

    # ---------- 核心：统一撮合 ----------
    def execute(self, date: pd.Timestamp, prices: Dict[str, float], actions_by_agent: Dict[str, dict]):
        \"\"\"
        :param date: 当前交易日
        :param prices: {symbol: close_price}
        :param actions_by_agent: {agent_name: {symbol: "BUY"/"SELL"/"HOLD" or weight(float)}}
        \"\"\"
        # 1) 将所有指令转换为“目标权重”
        target_weights: Dict[str, Dict[str, float]] = {}
        for agent, actions in actions_by_agent.items():
            pf = self.accounts[agent]
            # 计算当前权重
            nav = self._portfolio_value(pf, prices)
            curr_w = self._current_weights(pf, prices, nav)

            tw: Dict[str, float] = dict(curr_w)  # 默认维持现状
            for sym, instr in actions.items():
                if isinstance(instr, str):
                    s = instr.upper()
                    if s == "BUY":
                        tw[sym] = self.default_buy_w
                    elif s == "SELL":
                        tw[sym] = 0.0
                    elif s == "HOLD":
                        tw[sym] = curr_w.get(sym, 0.0)
                    else:
                        logger.warning(f"[{agent}] 未知指令 {sym}:{instr} → HOLD")
                        tw[sym] = curr_w.get(sym, 0.0)
                else:
                    # 目标权重
                    try:
                        w = float(instr)
                    except Exception:
                        w = curr_w.get(sym, 0.0)
                    tw[sym] = max(0.0, min(w, self.max_w))

            # 规范化：总权重不超过 1
            total_w = sum(tw.get(s, 0.0) for s in self.symbols)
            if total_w > 1.0:
                scale = 1.0 / total_w
                for s in self.symbols:
                    tw[s] = tw.get(s, 0.0) * scale

            target_weights[agent] = tw

        # 2) 根据目标权重 → 生成下单 shares，并做现金约束缩放
        for agent, tw in target_weights.items():
            pf = self.accounts[agent]
            nav = self._portfolio_value(pf, prices)
            # 目标价值
            tgt_value = {s: tw.get(s, 0.0) * nav for s in self.symbols}
            # 目标股数
            tgt_shares = {s: (tgt_value[s] / prices[s]) if prices.get(s) else 0.0 for s in self.symbols}
            # 订单股数 = 目标 - 当前
            curr_shares = {s: pf.positions.get(s, 0.0) for s in self.symbols}
            delta = {s: tgt_shares[s] - curr_shares[s] for s in self.symbols}

            # 先按目标下单，若现金不足则同比例缩放买单
            cash_needed, cash_released = self._estimate_cash_change(delta, prices)
            net_cash_change = cash_released - cash_needed  # 卖出带来现金 - 买入消耗现金
            if pf.cash + net_cash_change < 0:
                # 现金不足，缩放“买单”
                buy_cost = cash_needed
                if buy_cost > 0:
                    scale = max(0.0, (pf.cash + cash_released) / buy_cost)
                    for s in self.symbols:
                        if delta[s] > 0:
                            delta[s] *= scale

            # 3) 执行撮合（考虑费用/滑点）
            self._fill_orders(date, agent, pf, delta, prices)

            # 4) 记录 NAV
            nav_after = self._portfolio_value(pf, prices)
            pf.nav_history.append((date, nav_after))

    # ---------- 工具：当前权重 ----------
    def _current_weights(self, pf: Portfolio, prices: Dict[str, float], nav: float) -> Dict[str, float]:
        w = {}
        if nav <= 0:
            return {s: 0.0 for s in self.symbols}
        for s in self.symbols:
            sh = pf.positions.get(s, 0.0)
            px = prices.get(s, None)
            w[s] = (sh * px) / nav if px else 0.0
        return w

    # ---------- 工具：估算现金变化 ----------
    def _estimate_cash_change(self, delta_shares: Dict[str, float], prices: Dict[str, float]) -> Tuple[float, float]:
        \"\"\"返回: (买入所需现金, 卖出释放现金)，已考虑费用和滑点\"\"\"
        buy_cash = 0.0
        sell_cash = 0.0
        for s, dsh in delta_shares.items():
            px = prices.get(s)
            if px is None or dsh == 0:
                continue
            if dsh > 0:
                # 买入执行价：加滑点
                exec_px = px * (1.0 + self.slip)
                gross = dsh * exec_px
                fee = gross * self.fee
                buy_cash += gross + fee
            else:
                # 卖出执行价：减滑点
                exec_px = px * (1.0 - self.slip)
                gross = (-dsh) * exec_px
                fee = gross * self.fee
                sell_cash += gross - fee
        return buy_cash, sell_cash

    # ---------- 实际成交 ----------
    def _fill_orders(self, date: pd.Timestamp, agent: str, pf: Portfolio, delta_shares: Dict[str, float], prices: Dict[str, float]):
        for s, dsh in delta_shares.items():
            if abs(dsh) < 1e-9:
                continue
            px = prices.get(s)
            if px is None:
                continue

            if dsh > 0:  # buy
                exec_px = px * (1.0 + self.slip)
                gross = dsh * exec_px
                fee = gross * self.fee
                cash_change = -(gross + fee)
                side = "BUY"
                pf.positions[s] = pf.positions.get(s, 0.0) + dsh
                pf.cash += cash_change
            else:        # sell
                exec_px = px * (1.0 - self.slip)
                gross = (-dsh) * exec_px
                fee = gross * self.fee
                cash_change = (gross - fee)
                side = "SELL"
                pf.positions[s] = pf.positions.get(s, 0.0) + dsh  # dsh < 0
                # 不允许负仓（如出现浮点误差，截断）
                if pf.positions[s] < 0:
                    pf.positions[s] = 0.0
                pf.cash += cash_change

            self._trades.append({
                "date": date,
                "agent": agent,
                "symbol": s,
                "side": side,
                "price_exec": exec_px,
                "shares": float(dsh),
                "cash_after": float(pf.cash),
                "position_after_value": float(pf.positions.get(s, 0.0) * prices[s]),
            })

    # ---------- 导出 ----------
    def nav_dataframe(self) -> pd.DataFrame:
        \"\"\"返回所有选手的 NAV 序列 DataFrame\"\"\"
        dfs = []
        for agent, pf in self.accounts.items():
            if not pf.nav_history:
                continue
            df = pd.DataFrame(pf.nav_history, columns=["date", agent]).set_index("date")
            dfs.append(df)
        if not dfs:
            return pd.DataFrame()
        out = pd.concat(dfs, axis=1).sort_index()
        return out

    def trade_log(self) -> pd.DataFrame:
        if not self._trades:
            return pd.DataFrame(columns=self.trade_log_cols)
        df = pd.DataFrame(self._trades)
        df["date"] = pd.to_datetime(df["date"])
        return df.sort_values(["date", "agent", "symbol"])
"""
        return lines
    
    def arena(self):
        # src/arena.py    对抗主循环
        lines = """\"\"\"
src/arena.py
--------------------------------
对抗主循环：
- 读取 config.yaml
- 初始化 MarketFeed、VirtualBroker、各 Agent（PPO + DeepSeek）
- 在 test 区间逐日推进，统一撮合
- 输出报告到 reports/<timestamp>/
\"\"\"

import os
import yaml
import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np

# --- 运行程序初始化 python -m src.arena python虚拟境需要加入src文件夹路径 和读取环境变量 ---
import sys
from dotenv import load_dotenv
src_path = Path(__file__).resolve().parent
sys.path.append(str(src_path))
load_dotenv(str(src_path.parent / \'conf\' / \'.env\'))        # 自动加载 conf/.env 文件
# --- 运行程序初始化 python -m src.arena python虚拟境需要加入src文件夹路径 END ---

import pandas as pd
from loguru import logger

from market_feed import MarketFeed
from env_shared import VirtualBroker

# Agents
from agents.agent_ppo import PPOAgent
from agents.agent_deepseek import DeepSeekAgent


def load_config(path=\"conf/config.yaml\"):
    with open(path, \"r\", encoding=\"utf-8\") as f:
        return yaml.safe_load(f)


def ensure_dirs():
    Path("reports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)


def snapshot_prices(obs: dict) -> dict:
    \"\"\"从 obs 提取 {symbol: close}\"\"\"
    return {sym: float(v["close"]) for sym, v in obs.items()}


def run_once(cfg: dict):
    # -------- 初始化 --------
    ensure_dirs()
    logger.add(\"logs/arena.log\", rotation=\"1 MB\")

    symbols_file = Path(cfg["symbols_file"])
    with open(symbols_file, \"r\", encoding=\"utf-8\") as f:
        symbols = [x.strip() for x in f if x.strip()]

    test_start, test_end = cfg["split"]["test"]
    brk_cfg = cfg.get("broker", {})
    init_cash = float(brk_cfg.get("init_cash", 1_000_000))
    fee_bps = float(brk_cfg.get("fee_bps", 3))
    slippage_bps = float(brk_cfg.get("slippage_bps", 2))
    max_position_pct = float(brk_cfg.get("max_position_pct", 0.2))

    # 数据源
    feed = MarketFeed(symbols_file=str(symbols_file))
    feed.reset(test_start, test_end)  # 会自动 load_data

    # 券商与账户
    broker = VirtualBroker(
        symbols=symbols,
        init_cash=init_cash,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        max_position_pct=max_position_pct,
        default_buy_weight=min(0.1, max_position_pct),
    )

    # 注册选手（账户）
    agents_cfg = cfg.get(\"arena\", {}).get(\"agents\", [])
    agent_objs = {}
    for ag in agents_cfg:
        name = ag[\"name\"]
        broker.register_agent(name, init_cash=init_cash)
        if name.upper() == "PPO":
            agent_objs[name] = PPOAgent()
        elif name.upper() == \"DEEPSEEK\":
            model = ag.get(\"model\", \"deepseek-chat\")
            agent_objs[name] = DeepSeekAgent(model=model, temperature=0.2)
        else:
            # 默认当作 PPO 占位
            agent_objs[name] = PPOAgent()
            logger.warning(f"未识别的 agent {name}，默认使用 PPO 占位。")

    logger.info(f\"🧑‍⚖️ 开始竞赛：{', '.join(agent_objs.keys())}\")
    steps = 0
    flush_every = 10
    max_loop_count = 200      # 测试用, 不起作用就设置 None 或 0

    # 提前创建报告目录，允许循环中增量写入
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path(f"reports/{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # -------- 主循环（逐日）--------
    print('Loop start ......')
    while True:
        obs, done = feed.step()
        if obs is None:
            break
        prices = snapshot_prices(obs)

        # 所有选手在同一 obs 下出指令
        actions_by_agent = {}
        for name, ag in agent_objs.items():
            try:
                actions = ag.act(obs)
            except Exception as e:
                logger.exception(f"[{name}] act() 失败：{e}")
                # 失败时全 HOLD
                actions = {sym: "HOLD" for sym in prices.keys()}
            actions_by_agent[name] = actions

        # 统一撮合
        current_date = feed.active_dates[feed.idx - 1]  # 刚刚 step 出来的日期
        broker.execute(current_date, prices, actions_by_agent)

        steps += 1

        if steps % flush_every == 0 or done:
            _write_report_artifacts(broker, out_dir, include_plot=False)

        if done:
            break

        if max_loop_count is not None and max_loop_count > 1 and steps >= max_loop_count:
            break     # 测试用, 超过最大循环次数, 结束竞赛

    logger.info(f\"🏁 竞赛结束，共 {steps} 个交易日。\")

    # -------- 导出报告 --------
    _write_report_artifacts(broker, out_dir, include_plot=True)

    # 生成一个“latest”软链接（可选，Windows 跳过）
    latest_link = Path("reports/latest")
    try:
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(out_dir.resolve())
    except Exception:
        pass

    logger.info(f\"📦 报告已导出：{out_dir}\")
    return out_dir


def _write_report_artifacts(broker: VirtualBroker, out_dir: Path, *, include_plot: bool = True):
    out_dir.mkdir(parents=True, exist_ok=True)

    nav_df = broker.nav_dataframe()
    if not nav_df.empty:
        nav_csv = out_dir / "nav.csv"
        nav_df.to_csv(nav_csv)

        if include_plot:
            try:
                import matplotlib.pyplot as plt

                plt.figure()
                (nav_df / nav_df.iloc[0]).plot()
                plt.title("Normalized NAV")
                plt.xlabel("Date")
                plt.ylabel("NAV (normalized)")
                plt.tight_layout()
                plt.savefig(out_dir / "nav_curves.png")
                plt.close()
            except Exception as e:
                logger.warning(f"绘图失败：{e}")

    trades = broker.trade_log()
    trades.to_csv(out_dir / "trades.csv", index=False)

    summary = _compute_summary(nav_df)
    with open(out_dir / \"summary.json\", \"w\", encoding=\"utf-8\") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def _compute_summary(nav_df: pd.DataFrame) -> dict:
    summary = {}
    if nav_df is None or nav_df.empty:
        return summary

    for col in nav_df.columns:
        series = nav_df[col].dropna()
        if series.empty:
            continue
        ret = series.pct_change().dropna()
        periods = len(series)
        cagr = (series.iloc[-1] / series.iloc[0]) ** (252 / periods) - 1 if periods > 0 else 0.0
        vol = ret.std() * np.sqrt(252) if len(ret) > 1 else 0.0
        sharpe = (ret.mean() * 252) / vol if vol > 1e-12 else 0.0
        mdd = _max_drawdown(series.values)
        summary[col] = {
            \"final_nav\": float(series.iloc[-1]),
            \"CAGR\": float(cagr),
            \"ann_vol\": float(vol),
            \"sharpe\": float(sharpe),
            \"max_drawdown\": float(mdd),
        }

    return summary


def _max_drawdown(arr):
    arr = pd.Series(arr)
    roll_max = arr.cummax()
    drawdown = arr / roll_max - 1.0
    return drawdown.min()


def main():
    cfg = load_config(\"conf/config.yaml\")
    run_once(cfg)


if __name__ == \"__main__\":
    main()
"""
        return lines
    
    def evaluate(self):
        # src/evaluate.py （保存 summary.csv）
        lines = """# src/evaluate.py（修改示意）
import pandas as pd
import json
from pathlib import Path

def main():
    report_dir = Path("reports/latest")
    summary_json = report_dir / "summary.json"
    if not summary_json.exists():
        print("❌ 未找到 summary.json，请先运行 arena.py")
        return
    with open(summary_json, "r", encoding="utf-8") as f:
        summary = json.load(f)
    df = pd.DataFrame(summary).T
    df.index.name = "Agent"
    df.to_csv(report_dir / "summary.csv")
    print(f"✅ 已导出 summary.csv：{report_dir/'summary.csv'}")

if __name__ == "__main__":
    main()
"""
        return lines
    
    def web_dashboard_utils(self):
        # src/web_dashboard_utils.py.    这个模块统一读取 reports/ 目录并整理数据。
        lines = """# src/web_dashboard_utils.py
import pandas as pd
from pathlib import Path
import json

def load_latest_report(base_dir="reports"):
    base = Path(base_dir)
    if not base.exists():
        raise FileNotFoundError("reports 文件夹不存在")
    subdirs = [d for d in base.iterdir() if d.is_dir()]
    if not subdirs:
        raise FileNotFoundError("reports 下无结果")
    latest = max(subdirs, key=lambda d: d.stat().st_mtime)
    return latest

def load_summary(report_dir: Path):
    f = report_dir / "summary.csv"
    if f.exists():
        df = pd.read_csv(f, index_col="Agent")
    else:
        js = json.load(open(report_dir / "summary.json", "r", encoding="utf-8"))
        df = pd.DataFrame(js).T
    return df

def load_nav(report_dir: Path):
    f = report_dir / "nav.csv"
    return pd.read_csv(f, index_col="date", parse_dates=True)

def load_trades(report_dir: Path):
    f = report_dir / "trades.csv"
    if f.exists():
        return pd.read_csv(f, parse_dates=["date"])
    return pd.DataFrame()
"""
        return lines


class AgentsFilesContent:
    """
    src/agents/ 文件和内容
    """
    def __init__(self):
        self.cls_compute = ComputePathContent()        #计算内容和路径
        self.file_names = ['agent_deepseek', ]
        self.project_path = None

    def main_write_files(self, project_path:Path):
        # 文件路径和内容
        self.project_path = project_path
        generated_files_paths = []
        for fn in self.file_names:
            file_path = self.cls_compute._compute_file_path(self.project_path, fn, dir_names=('src', 'agents',))
            content = self.cls_compute._compute_content(self, fn)
            self.cls_compute._write_file(file_path, content)    # 保存文件
            generated_files_paths.append(file_path)
        return generated_files_paths

    def agent_deepseek(self):
        # src/agents/agent_deepseek.py
        lines = """# DeepSeek 智能体 (API 调用)
import json
import os
from typing import Iterable, Mapping

from openai import OpenAI


class DeepSeekAgent:
    _SYSTEM_PROMPT = (
        "你是一个量化交易助手。请根据输入的 JSON 市场数据，"
        "输出一个 JSON 对象，键为股票代码，值只能是 BUY、SELL 或 HOLD。"
        "不要包含额外说明或 Markdown。"
    )

    def __init__(self, model="deepseek-chat", temperature=0.3):
        key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/"
        base_url = base_url.strip()
        if not key:
            print(f"⚠️ 未设置 DEEPSEEK_API_KEY; url:{base_url};")
        self.client = OpenAI(api_key=key, base_url=base_url)
        self.model = model
        self.temperature = temperature

    def act(self, obs: Mapping[str, dict]):
        symbols = list(obs.keys())
        default_decisions = self._default_actions(symbols)
        try:
            user_payload = json.dumps(obs, ensure_ascii=False)
            params = dict(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._SYSTEM_PROMPT},
                    {"role": "user", "content": user_payload},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            try:
                resp = self.client.chat.completions.create(**params)
            except TypeError:
                params.pop("response_format", None)
                resp = self.client.chat.completions.create(**params)
            reply = self._extract_reply(resp)
            decisions = self._parse_decisions(reply, symbols)
            if not decisions:
                self._log_unparsed_response(resp, reply, symbols, obs)
                return default_decisions
            return decisions
        except Exception as e:
            print("⚠️ DeepSeek 调用失败:", e)
            return default_decisions

    @staticmethod
    def _default_actions(symbols: Iterable[str]):
        return {sym: "HOLD" for sym in symbols}

    @staticmethod
    def _parse_decisions(reply: str, symbols: Iterable[str]):
        if not reply:
            return None
        data = None
        try:
            data = json.loads(reply)
        except json.JSONDecodeError:
            start = reply.find("{")
            end = reply.rfind("}")
            if start != -1 and end != -1 and end > start:
                fragment = reply[start : end + 1]
                try:
                    data = json.loads(fragment)
                except json.JSONDecodeError:
                    data = None

        if isinstance(data, list):
            merged = {}
            for item in data:
                if isinstance(item, dict):
                    merged.update(item)
            data = merged if merged else None

        if not isinstance(data, dict):
            return None

        decisions = {}
        for sym in symbols:
            value = data.get(sym)
            if isinstance(value, dict) and "action" in value:
                value = value.get("action")
            action = str(value or "").strip().upper()
            if action not in {"BUY", "SELL", "HOLD"}:
                action = "HOLD"
            decisions[sym] = action
        return decisions

    @staticmethod
    def _extract_reply(resp) -> str:
        try:
            choice = resp.choices[0]
        except Exception:
            return ""

        message = getattr(choice, "message", None) or {}

        content = None
        if isinstance(message, dict):
            content = message.get("content")
        else:
            content = getattr(message, "content", None)

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    if "text" in item and item["text"] is not None:
                        parts.append(str(item["text"]))
                    elif "output" in item and item["output"] is not None:
                        parts.append(str(item["output"]))
                    elif "json" in item and item["json"] is not None:
                        try:
                            parts.append(json.dumps(item["json"], ensure_ascii=False))
                        except Exception:
                            parts.append(str(item["json"]))
                    else:
                        parts.append(str(item))
                else:
                    parts.append(str(item))
            return "".join(parts).strip()

        if content is None:
            # 兼容某些 SDK 使用 message='content' 字段的情况
            if isinstance(message, dict):
                raw = message.get("message")
                if isinstance(raw, dict):
                    txt = raw.get("content")
                    if isinstance(txt, str):
                        return txt.strip()

        # 退一步尝试整个 choice/dict
        if hasattr(choice, "model_dump"):
            blob = choice.model_dump()
        elif isinstance(choice, dict):
            blob = choice
        else:
            blob = {}
        return str(blob).strip()

    def _log_unparsed_response(self, resp, reply: str, symbols: Iterable[str], obs: Mapping[str, dict]):
        pass
        # print("⚠️ DeepSeek 响应无法解析，全部 HOLD。原始响应:", reply)
        # print("⚠️ DeepSeek 原始响应结构:", self._safe_dump_response(resp))
        # print("⚠️ 当前观测样本:", self._preview_obs(obs))

    @staticmethod
    def _safe_dump_response(resp) -> str:
        try:
            if hasattr(resp, "model_dump"):
                data = resp.model_dump()
            elif isinstance(resp, dict):
                data = resp
            else:
                data = resp.__dict__
        except Exception:
            try:
                return repr(resp)
            except Exception:
                return "<unprintable response>"

        try:
            return json.dumps(data, ensure_ascii=False, indent=2, default=str)
        except Exception:
            return repr(data)

    @staticmethod
    def _preview_obs(obs: Mapping[str, dict], limit: int = 2) -> dict:
        sample = {}
        for i, (sym, info) in enumerate(obs.items()):
            if i >= limit:
                break
            sample[sym] = info
        return sample
"""
        return lines

class MainFilesContent:
    """
    入口文件和内容
    """
    def __init__(self):
        self.cls_compute = ComputePathContent()        #计算内容和路径
        self.file_names = ['web_dashboard', ]
        self.project_path = None

    def main_write_files(self, project_path:Path):
        # 文件路径和内容
        self.project_path = project_path
        generated_files_paths = []
        for fn in self.file_names:
            file_path = self.cls_compute._compute_file_path(self.project_path, fn, dir_names=None)
            content = self.cls_compute._compute_content(self, fn)
            self.cls_compute._write_file(file_path, content)    # 保存文件
            generated_files_paths.append(file_path)
        return generated_files_paths

    def web_dashboard(self):
        # web_dashboard.py（Streamlit 主界面）
        lines = """# web_dashboard.py
import streamlit as st
import plotly.express as px
import pandas as pd
from src.web_dashboard_utils import load_latest_report, load_summary, load_nav, load_trades

st.set_page_config(page_title="AI 模型对抗平台", layout="wide")

st.title("🏆 AI 模型虚拟交易竞赛平台 Dashboard")

# --- 载入数据 ---
try:
    report_dir = load_latest_report()
    st.sidebar.success(f"当前报告：{report_dir.name}")
    summary_df = load_summary(report_dir)
    nav_df = load_nav(report_dir)
    trades_df = load_trades(report_dir)
except Exception as e:
    st.error(f"加载报告失败：{e}")
    st.stop()

# --- 概览 ---
st.header("📈 收益曲线")
fig = px.line(nav_df / nav_df.iloc[0], title="归一化收益曲线 (起点=1.0)")
st.plotly_chart(fig, use_container_width=True)

# --- 绩效指标 ---
st.header("📊 模型绩效指标")
st.dataframe(summary_df.style.format("{:.3f}"))

# --- 交易日志 ---
st.header("💼 交易日志")
if not trades_df.empty:
    st.dataframe(trades_df.tail(20))
else:
    st.info("暂无交易记录")

# --- 历史报告选择 ---
st.sidebar.header("报告历史")
import os
import glob
reports = sorted(glob.glob("reports/*/summary.csv"), reverse=True)
sel = st.sidebar.selectbox("选择报告", reports)
if sel:
    df_old = pd.read_csv(sel, index_col="Agent")
    st.sidebar.dataframe(df_old)

# --- 项目运行方法(激活环境后执行): streamlit run web_dashboard.py ---

"""
        return lines


# === 创建目录 ===
for d in dirs:
    path = root / d
    path.mkdir(parents=True, exist_ok=True)

# === 写文件 ===
for rel_path, content in files_content.items():
    file_path = root / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# === 写src文件, 主文件 ===
cls_src_files = SrcFilesContent()
cls_src_files.main_write_files(project_path=root)
cls_agents_files = AgentsFilesContent()
cls_agents_files.main_write_files(project_path=root)
cls_main_files = MainFilesContent()
cls_main_files.main_write_files(project_path=root)

# === run.sh 权限 ===
os.chmod(root / "run.sh", 0o755)

print(f"✅ 项目结构已生成在: {root.resolve()}")


# 执行方法:
#   1. 创建文件夹 arena_qlib_finrl
#                       |__ venv
#                       |__ tools
#   2. 创建python虚拟环境: cd arena_qlib_finrl/venv && python3 -m venv . && cd ..
#   3. 激活虚拟环境: source venv/bin/activate
#   4. 创建基础文件和文件夹: python tools/generate_project_structure.py
#   5. 安装依赖和初始化数据: 
#           pip install -r requirements.txt
#           python -m src.qlib_init
#           python -m src.arena
#   6. 启动: streamlit run web_dashboard.py
