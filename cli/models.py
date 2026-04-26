from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"


class MarketType(str, Enum):
    US = "us"
    KR = "kr"
    CN = "cn"


MARKET_VENDOR_CONFIG = {
    "us": {
        "description": "US Stock Market (NYSE, NASDAQ, AMEX)",
        "data_vendors": {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "yfinance",
            "news_data": "yfinance",
            "fund_data": "yfinance",
        },
        "ticker_examples": ["AAPL", "MSFT", "GOOGL", "SPY", "QQQ"],
    },
    "kr": {
        "description": "Korean Stock Market (KRX)",
        "data_vendors": {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "yfinance",
            "news_data": "yfinance",
            "dart_data": "opendart",
            "fund_data": "yfinance",
        },
        "ticker_examples": ["005930", "000660", "035420"],
    },
    "cn": {
        "description": "China A-Share Market (Shanghai, Shenzhen)",
        "data_vendors": {
            "core_stock_apis": "akshare",
            "technical_indicators": "akshare",
            "fundamental_data": "akshare",
            "news_data": "akshare",
            "fund_data": "akshare",
        },
        "ticker_examples": ["600519", "000001", "300750", "510300", "110022"],
    },
}
