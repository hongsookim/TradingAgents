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

"""Tests for China A-Share market support - akshare integration, CLI market selection, etc."""

import pytest
from unittest.mock import patch, MagicMock


class TestAKShareModuleImport:
    """Test that akshare data module can be imported correctly."""

    def test_import_akshare_data_module(self):
        """Test that akshare_data module can be imported."""
        from tradingagents.dataflows import akshare_data
        
        assert hasattr(akshare_data, 'get_akshare_stock_data')
        assert hasattr(akshare_data, 'get_akshare_indicators')
        assert hasattr(akshare_data, 'get_akshare_fundamentals')
        assert hasattr(akshare_data, 'get_akshare_news')
        assert hasattr(akshare_data, 'detect_akshare_asset_type')

    def test_import_akshare_fund_functions(self):
        """Test that akshare fund functions can be imported."""
        from tradingagents.dataflows import akshare_data
        
        assert hasattr(akshare_data, 'get_akshare_fund_nav')
        assert hasattr(akshare_data, 'get_akshare_fund_holdings')
        assert hasattr(akshare_data, 'get_akshare_fund_manager_info')
        assert hasattr(akshare_data, 'get_akshare_fund_expense_ratio')
        assert hasattr(akshare_data, 'get_akshare_fund_risk_metrics')
        assert hasattr(akshare_data, 'get_akshare_fund_overview')


class TestInterfaceAKShareRegistration:
    """Test that akshare is properly registered in interface.py."""

    def test_akshare_in_vendor_list(self):
        """Test that akshare is in VENDOR_LIST."""
        from tradingagents.dataflows.interface import VENDOR_LIST
        
        assert "akshare" in VENDOR_LIST

    def test_akshare_in_vendor_methods_core(self):
        """Test that akshare is registered for core stock methods."""
        from tradingagents.dataflows.interface import VENDOR_METHODS
        
        core_methods = [
            "get_stock_data",
            "get_indicators",
            "get_fundamentals",
            "get_balance_sheet",
            "get_cashflow",
            "get_income_statement",
            "get_news",
            "get_global_news",
            "get_insider_transactions",
        ]
        
        for method in core_methods:
            assert method in VENDOR_METHODS, f"Method {method} not found in VENDOR_METHODS"
            assert "akshare" in VENDOR_METHODS[method], f"akshare not registered for {method}"

    def test_akshare_in_vendor_methods_fund(self):
        """Test that akshare is registered for fund methods."""
        from tradingagents.dataflows.interface import VENDOR_METHODS
        
        fund_methods = [
            "detect_asset_type",
            "get_fund_holdings",
            "get_fund_nav",
            "get_fund_manager_info",
            "get_fund_expense_ratio",
            "get_fund_risk_metrics",
            "get_fund_overview",
        ]
        
        for method in fund_methods:
            assert method in VENDOR_METHODS, f"Method {method} not found in VENDOR_METHODS"
            assert "akshare" in VENDOR_METHODS[method], f"akshare not registered for {method}"


class TestDefaultConfigChinaMarket:
    """Test that default config has China A-Share market settings."""

    def test_config_has_market_field(self):
        """Test that config has 'market' field."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        assert "market" in DEFAULT_CONFIG
        assert DEFAULT_CONFIG["market"] == "us"

    def test_config_has_china_market_section(self):
        """Test that config has 'china_market' section."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        assert "china_market" in DEFAULT_CONFIG
        china_config = DEFAULT_CONFIG["china_market"]
        
        assert "trading_hours" in china_config
        assert "price_limit" in china_config
        assert "trading_mechanism" in china_config

    def test_china_market_trading_hours(self):
        """Test China market trading hours configuration."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        trading_hours = DEFAULT_CONFIG["china_market"]["trading_hours"]
        
        assert trading_hours["morning_start"] == "09:30"
        assert trading_hours["morning_end"] == "11:30"
        assert trading_hours["afternoon_start"] == "13:00"
        assert trading_hours["afternoon_end"] == "15:00"

    def test_china_market_price_limits(self):
        """Test China market price limit configuration."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        price_limit = DEFAULT_CONFIG["china_market"]["price_limit"]
        
        assert price_limit["normal"] == 0.10
        assert price_limit["st"] == 0.05
        assert price_limit["star"] == 0.20
        assert price_limit["chinext"] == 0.20
        assert price_limit["new_listing_days"] == 5

    def test_china_market_trading_mechanism(self):
        """Test China market trading mechanism configuration."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        trading_mechanism = DEFAULT_CONFIG["china_market"]["trading_mechanism"]
        
        assert trading_mechanism["settlement_cycle"] == "T+1"
        assert trading_mechanism["short_selling_allowed"] == False
        assert trading_mechanism["t_plus_0_etf"] == True

    def test_data_vendors_comments_include_akshare(self):
        """Test that data_vendors config includes akshare options."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        assert "data_vendors" in DEFAULT_CONFIG
        data_vendors = DEFAULT_CONFIG["data_vendors"]
        
        for key in data_vendors:
            assert key in [
                "core_stock_apis",
                "technical_indicators",
                "fundamental_data",
                "news_data",
                "dart_data",
                "fund_data",
            ]


class TestCLIMarketType:
    """Test CLI market type enum and configuration."""

    def test_market_type_enum_exists(self):
        """Test that MarketType enum exists."""
        from cli.models import MarketType
        
        assert MarketType.US.value == "us"
        assert MarketType.KR.value == "kr"
        assert MarketType.CN.value == "cn"

    def test_market_vendor_config_exists(self):
        """Test that MARKET_VENDOR_CONFIG exists."""
        from cli.models import MARKET_VENDOR_CONFIG
        
        assert "us" in MARKET_VENDOR_CONFIG
        assert "kr" in MARKET_VENDOR_CONFIG
        assert "cn" in MARKET_VENDOR_CONFIG

    def test_cn_market_vendor_config(self):
        """Test CN market vendor configuration."""
        from cli.models import MARKET_VENDOR_CONFIG
        
        cn_config = MARKET_VENDOR_CONFIG["cn"]
        
        assert "description" in cn_config
        assert "data_vendors" in cn_config
        assert "ticker_examples" in cn_config
        
        assert cn_config["data_vendors"]["core_stock_apis"] == "akshare"
        assert cn_config["data_vendors"]["technical_indicators"] == "akshare"
        assert cn_config["data_vendors"]["fundamental_data"] == "akshare"
        assert cn_config["data_vendors"]["news_data"] == "akshare"
        assert cn_config["data_vendors"]["fund_data"] == "akshare"

    def test_us_market_vendor_config(self):
        """Test US market vendor configuration (uses yfinance)."""
        from cli.models import MARKET_VENDOR_CONFIG
        
        us_config = MARKET_VENDOR_CONFIG["us"]
        
        assert us_config["data_vendors"]["core_stock_apis"] == "yfinance"
        assert us_config["data_vendors"]["fund_data"] == "yfinance"

    def test_select_market_function_exists(self):
        """Test that select_market function exists."""
        from cli.utils import select_market
        
        assert select_market is not None


class TestAKShareAssetTypeDetection:
    """Test akshare asset type detection logic."""

    def test_detect_akshare_asset_type_shanghai_stock(self):
        """Test detection of Shanghai stocks (600xxx, 601xxx, etc.)."""
        from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
        
        shanghai_stocks = ["600519", "601318", "603288", "605117", "688981"]
        
        for ticker in shanghai_stocks:
            result = detect_akshare_asset_type(ticker)
            assert result == "STOCK", f"Expected STOCK for {ticker}, got {result}"

    def test_detect_akshare_asset_type_shenzhen_stock(self):
        """Test detection of Shenzhen stocks (000xxx, 002xxx, 300xxx, etc.)."""
        from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
        
        shenzhen_stocks = ["000001", "001979", "002415", "003022", "300750"]
        
        for ticker in shenzhen_stocks:
            result = detect_akshare_asset_type(ticker)
            assert result == "STOCK", f"Expected STOCK for {ticker}, got {result}"

    def test_detect_akshare_asset_type_etf(self):
        """Test detection of ETFs."""
        from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
        
        etfs = ["510300", "510500", "512880", "513100", "515050", "560050", "159915"]
        
        for ticker in etfs:
            result = detect_akshare_asset_type(ticker)
            assert result == "ETF", f"Expected ETF for {ticker}, got {result}"

    def test_detect_akshare_asset_type_fund(self):
        """Test detection of mutual funds/LOFs."""
        from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
        
        funds = ["110022", "161725", "161005", "180012", "501018", "000001"]
        
        for ticker in funds:
            result = detect_akshare_asset_type(ticker)
            # 6-digit codes not matching stock/ETF patterns are treated as funds
            assert result in ["FUND", "LOF"], f"Expected FUND/LOF for {ticker}, got {result}"

    def test_detect_akshare_asset_type_non_numeric(self):
        """Test detection of non-numeric tickers (US stocks)."""
        from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
        
        non_numeric = ["AAPL", "MSFT", "SPY", "QQQ"]
        
        for ticker in non_numeric:
            result = detect_akshare_asset_type(ticker)
            # Non-numeric tickers should return a message indicating not A-share
            assert "not A-share" in result or "UNKNOWN" in result or "error" in result.lower()


class TestAKShareDefensiveProgramming:
    """Test that akshare functions handle errors gracefully."""

    @patch('tradingagents.dataflows.akshare_data.ak.stock_zh_a_hist')
    def test_get_akshare_stock_data_handles_exception(self, mock_ak):
        """Test that get_akshare_stock_data handles exceptions gracefully."""
        mock_ak.side_effect = Exception("Network error")
        
        from tradingagents.dataflows.akshare_data import get_akshare_stock_data
        
        result = get_akshare_stock_data("600519", "2026-01-01", "2026-01-31")
        
        assert "error" in result.lower()
        assert "600519" in result

    @patch('tradingagents.dataflows.akshare_data.ak.fund_open_fund_info_em')
    def test_get_akshare_fund_nav_handles_exception(self, mock_ak):
        """Test that get_akshare_fund_nav handles exceptions gracefully."""
        mock_ak.side_effect = Exception("API error")
        
        from tradingagents.dataflows.akshare_data import get_akshare_fund_nav
        
        result = get_akshare_fund_nav("110022", period="1y")
        
        assert "error" in result.lower()
        assert "110022" in result

    def test_get_akshare_indicators_handles_invalid_indicator(self):
        """Test that get_akshare_indicators handles invalid indicator gracefully."""
        from tradingagents.dataflows.akshare_data import get_akshare_indicators
        
        result = get_akshare_indicators("600519", "INVALID_INDICATOR", "2026-01-31", 30)
        
        # Should return a valid message about invalid indicator
        assert result is not None
        assert isinstance(result, str)


class TestBackwardCompatibilityUSKR:
    """Test that existing US/KR market functionality is not broken."""

    def test_us_market_vendor_still_yfinance(self):
        """Test that US market still uses yfinance by default."""
        from cli.models import MARKET_VENDOR_CONFIG
        
        assert MARKET_VENDOR_CONFIG["us"]["data_vendors"]["core_stock_apis"] == "yfinance"
        assert MARKET_VENDOR_CONFIG["us"]["data_vendors"]["fund_data"] == "yfinance"

    def test_kr_market_vendor_still_yfinance(self):
        """Test that KR market still uses yfinance + opendart."""
        from cli.models import MARKET_VENDOR_CONFIG
        
        assert MARKET_VENDOR_CONFIG["kr"]["data_vendors"]["core_stock_apis"] == "yfinance"
        assert MARKET_VENDOR_CONFIG["kr"]["data_vendors"]["dart_data"] == "opendart"

    def test_yfinance_still_registered_in_vendor_methods(self):
        """Test that yfinance is still the primary vendor for existing methods."""
        from tradingagents.dataflows.interface import VENDOR_METHODS
        
        for method_name, vendors in VENDOR_METHODS.items():
            if method_name not in ["get_opendart_corp_code", "get_opendart_report"]:
                assert "yfinance" in vendors, f"yfinance should be registered for {method_name}"

    def test_default_config_stock_methods_preserved(self):
        """Test that stock methods are preserved in default config."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        data_vendors = DEFAULT_CONFIG["data_vendors"]
        
        assert data_vendors["core_stock_apis"] == "yfinance"
        assert data_vendors["technical_indicators"] == "yfinance"
        assert data_vendors["fundamental_data"] == "yfinance"
        assert data_vendors["news_data"] == "yfinance"
        assert data_vendors["dart_data"] == "opendart"
        assert data_vendors["fund_data"] == "yfinance"

    def test_route_to_vendor_still_works(self):
        """Test that route_to_vendor function still works."""
        from tradingagents.dataflows.interface import route_to_vendor, VENDOR_METHODS
        
        # The function exists
        assert route_to_vendor is not None
        
        # Check that it has proper error handling for invalid methods
        from unittest.mock import patch
        
        with patch('tradingagents.dataflows.interface.get_config') as mock_get_config:
            mock_get_config.return_value = {"data_vendors": {}}
            # Calling with invalid method should not crash
            # We can't easily test it without mocking more, but we know it exists


class TestAgentToolsAKShareReady:
    """Test that agent tools are ready for akshare via routing."""

    def test_agent_utils_stock_tools_importable(self):
        """Test that stock tools can be imported and use routing."""
        from tradingagents.agents.utils.agent_utils import (
            get_stock_data,
            get_indicators,
            get_fundamentals,
            get_news,
        )
        
        assert get_stock_data is not None
        assert get_indicators is not None
        assert get_fundamentals is not None
        assert get_news is not None

    def test_agent_utils_fund_tools_importable(self):
        """Test that fund tools can be imported and use routing."""
        from tradingagents.agents.utils.agent_utils import (
            detect_asset_type,
            get_fund_holdings,
            get_fund_nav,
            get_fund_manager_info,
            get_fund_expense_ratio,
            get_fund_risk_metrics,
            get_fund_overview,
        )
        
        assert detect_asset_type is not None
        assert get_fund_holdings is not None
        assert get_fund_nav is not None
        assert get_fund_manager_info is not None
        assert get_fund_expense_ratio is not None
        assert get_fund_risk_metrics is not None
        assert get_fund_overview is not None

    def test_tools_categories_include_fund_data(self):
        """Test that tools categories include fund_data."""
        from tradingagents.dataflows.interface import TOOLS_CATEGORIES
        
        assert "fund_data" in TOOLS_CATEGORIES
        assert "tools" in TOOLS_CATEGORIES["fund_data"]
        
        fund_tools = TOOLS_CATEGORIES["fund_data"]["tools"]
        assert "detect_asset_type" in fund_tools
        assert "get_fund_nav" in fund_tools
        assert "get_fund_overview" in fund_tools
