# Copyright 2026 herald.k, HongSoo Kim
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # Market selection: "us" (US stocks), "kr" (Korean stocks), "cn" (China A-shares)
    "market": "us",
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.4",
    "quick_think_llm": "gpt-5.4",
    "backend_url": "https://coder.api.visioncoder.cn/v1",
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": "high",    # "medium", "high", "low"
    "anthropic_effort": None,

    "output_language": "Chinese",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: alpha_vantage, yfinance, akshare
        "technical_indicators": "yfinance",  # Options: alpha_vantage, yfinance, akshare
        "fundamental_data": "yfinance",      # Options: alpha_vantage, yfinance, akshare
        "news_data": "yfinance",             # Options: alpha_vantage, yfinance, akshare
        "dart_data": "opendart",             # Options: opendart
        "fund_data": "yfinance",             # Options: yfinance, akshare (ETF/Mutual Fund data)
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
    # YFinance retry/backoff configuration
    "yfinance_retry": {
        "max_retries": 3,         # Number of retry attempts before giving up
        "base_delay": 2.0,        # Initial backoff delay in seconds
        "max_delay": 60.0,        # Maximum backoff delay cap in seconds
        "backoff_factor": 2.0,    # Exponential backoff multiplier (2s → 4s → 8s)
    },
    # Data cache TTL in seconds (0 to disable caching for a category)
    "cache_ttl": {
        "fundamentals": 3600,          # 1 hour
        "financial_statements": 3600,  # 1 hour
        "news": 900,                   # 15 minutes
        "insider_transactions": 3600,  # 1 hour
        "fund_data": 3600,             # 1 hour (ETF/Mutual Fund data)
    },
    # China A-share market specific configuration
    "china_market": {
        # A-share stock code rules:
        # - Shanghai: 600xxx, 601xxx, 603xxx, 605xxx, 688xxx (STAR Market)
        # - Shenzhen: 000xxx, 001xxx, 002xxx, 003xxx (Main), 300xxx (ChiNext)
        # A-share ETF code rules:
        # - Shanghai: 510xxx, 511xxx, 512xxx, 513xxx, 515xxx, 516xxx, 518xxx, 56xxx
        # - Shenzhen: 159xxx
        # A-share Mutual Fund code rules:
        # - 16xxx (LOF), 18xxx, 50xxx, 0xxxx (non-stock codes)
        "trading_hours": {
            "morning_start": "09:30",
            "morning_end": "11:30",
            "afternoon_start": "13:00",
            "afternoon_end": "15:00",
        },
        # Price limit rules (A-share)
        "price_limit": {
            "normal": 0.10,      # 10% price limit for normal stocks
            "st": 0.05,           # 5% price limit for ST stocks
            "star": 0.20,         # 20% price limit for STAR Market (688xxx)
            "chinext": 0.20,      # 20% price limit for ChiNext (300xxx)
            "new_listing_days": 5,  # No price limit for first 5 trading days after listing
        },
        # Trading mechanism
        "trading_mechanism": {
            "settlement_cycle": "T+1",  # T+1 settlement for A-shares
            "short_selling_allowed": False,  # Limited short selling via margin trading
            "t_plus_0_etf": True,  # Some ETFs allow T+0 trading
        },
    },
    # Investment persona configuration
    # Options: None, "warren_buffett", "ray_dalio", "peter_lynch"
    "persona": None,
    # Broker execution configuration
    "broker": {
        "enabled": False,  # Master switch for trade execution
        "provider": "kis",  # Broker provider: "kis" (Korea), "eastmoney" (China)
        "mode": "paper",  # "paper" (모의투자) or "real" (실투자)
        "kis_app_key": None,  # KIS APP_KEY (or env: KIS_APP_KEY)
        "kis_app_secret": None,  # KIS APP_SECRET (or env: KIS_APP_SECRET)
        "kis_account_no": None,  # Account number "XXXXXXXX-XX" (or env: KIS_ACCOUNT_NO)
        # China broker configuration (for future integration)
        "eastmoney_app_key": None,  # East Money APP_KEY
        "eastmoney_app_secret": None,  # East Money APP_SECRET
        "default_order_type": "market",  # "market" or "limit"
        "default_quantity": None,  # Fixed quantity per trade (None = use percentage)
        "default_position_pct": 0.05,  # 5% of portfolio per trade
        "safety": {
            "max_position_pct": 0.10,  # Max 10% of portfolio in one stock
            "max_order_amount": 5_000_000,  # Max 5M KRW per order (or CNY for China market)
            "daily_loss_limit": -500_000,  # Stop trading if daily loss exceeds 500K KRW
            "enforce_market_hours": True,  # Only trade during exchange hours
            "require_confirmation": True,  # Prompt before real trades
            # A-share specific safety
            "enforce_price_limits": True,  # Enforce A-share price limits (10% normal, 20% STAR/ChiNext)
            "st_stock_warning": True,  # Warn before trading ST stocks
        },
    },
}
