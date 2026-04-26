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

"""Tests for fund data flows - ETF and mutual fund data retrieval."""

import pytest
from unittest.mock import patch, MagicMock


class TestFundDataToolsImport:
    """Test that fund data tools can be imported correctly."""

    def test_import_fund_data_tools(self):
        """Test that fund_data_tools module can be imported."""
        from tradingagents.agents.utils import fund_data_tools
        
        assert hasattr(fund_data_tools, 'detect_asset_type')
        assert hasattr(fund_data_tools, 'get_fund_holdings')
        assert hasattr(fund_data_tools, 'get_fund_nav')
        assert hasattr(fund_data_tools, 'get_fund_manager_info')
        assert hasattr(fund_data_tools, 'get_fund_expense_ratio')
        assert hasattr(fund_data_tools, 'get_fund_risk_metrics')
        assert hasattr(fund_data_tools, 'get_fund_overview')

    def test_import_agent_utils_exports(self):
        """Test that agent_utils exports fund tools."""
        from tradingagents.agents.utils import agent_utils
        
        assert hasattr(agent_utils, 'detect_asset_type')
        assert hasattr(agent_utils, 'get_fund_holdings')
        assert hasattr(agent_utils, 'get_fund_nav')
        assert hasattr(agent_utils, 'get_fund_manager_info')
        assert hasattr(agent_utils, 'get_fund_expense_ratio')
        assert hasattr(agent_utils, 'get_fund_risk_metrics')
        assert hasattr(agent_utils, 'get_fund_overview')

    def test_import_fund_analyst(self):
        """Test that fund_analyst can be imported."""
        from tradingagents.agents.analysts import fund_analyst
        
        assert hasattr(fund_analyst, 'create_fund_analyst')
        assert hasattr(fund_analyst, 'create_dynamic_analyst_router')

    def test_import_agents_init_exports(self):
        """Test that agents __init__ exports fund analyst."""
        from tradingagents.agents import (
            create_fund_analyst,
            create_dynamic_analyst_router,
        )
        
        assert create_fund_analyst is not None
        assert create_dynamic_analyst_router is not None


class TestInterfaceFundMethods:
    """Test that interface.py has fund methods registered."""

    def test_fund_data_category_exists(self):
        """Test that fund_data category exists in TOOLS_CATEGORIES."""
        from tradingagents.dataflows.interface import TOOLS_CATEGORIES
        
        assert "fund_data" in TOOLS_CATEGORIES
        assert "tools" in TOOLS_CATEGORIES["fund_data"]
        assert "description" in TOOLS_CATEGORIES["fund_data"]

    def test_fund_tools_in_category(self):
        """Test that all fund tools are listed in the category."""
        from tradingagents.dataflows.interface import TOOLS_CATEGORIES
        
        fund_tools = TOOLS_CATEGORIES["fund_data"]["tools"]
        
        expected_tools = [
            "detect_asset_type",
            "get_fund_holdings",
            "get_fund_nav",
            "get_fund_manager_info",
            "get_fund_expense_ratio",
            "get_fund_risk_metrics",
            "get_fund_overview",
        ]
        
        for tool in expected_tools:
            assert tool in fund_tools, f"Expected tool {tool} not found in fund_data category"

    def test_fund_methods_in_vendor_methods(self):
        """Test that all fund methods are in VENDOR_METHODS."""
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
            assert method in VENDOR_METHODS, f"Expected method {method} not found in VENDOR_METHODS"
            assert "yfinance" in VENDOR_METHODS[method], f"yfinance not registered for {method}"


class TestAgentStateFundFields:
    """Test that AgentState has fund-related fields."""

    def test_agent_state_has_asset_type(self):
        """Test that AgentState has asset_type field."""
        from tradingagents.agents.utils.agent_states import AgentState
        
        assert "asset_type" in AgentState.__annotations__

    def test_agent_state_has_fund_overview_report(self):
        """Test that AgentState has fund_overview_report field."""
        from tradingagents.agents.utils.agent_states import AgentState
        
        assert "fund_overview_report" in AgentState.__annotations__


class TestDefaultConfigFundSettings:
    """Test that default config has fund-related settings."""

    def test_data_vendors_has_fund_data(self):
        """Test that fund_data is in data_vendors config."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        assert "data_vendors" in DEFAULT_CONFIG
        assert "fund_data" in DEFAULT_CONFIG["data_vendors"]
        assert DEFAULT_CONFIG["data_vendors"]["fund_data"] == "yfinance"

    def test_cache_ttl_has_fund_data(self):
        """Test that fund_data is in cache_ttl config."""
        from tradingagents.default_config import DEFAULT_CONFIG
        
        assert "cache_ttl" in DEFAULT_CONFIG
        assert "fund_data" in DEFAULT_CONFIG["cache_ttl"]
        assert DEFAULT_CONFIG["cache_ttl"]["fund_data"] == 3600


class TestPropagationInitialState:
    """Test that propagation creates initial state with fund fields."""

    def test_create_initial_state_has_asset_type(self):
        """Test that initial state includes asset_type."""
        from tradingagents.graph.propagation import Propagator
        
        propagator = Propagator()
        state = propagator.create_initial_state("AAPL", "2026-01-01")
        
        assert "asset_type" in state
        assert state["asset_type"] == ""

    def test_create_initial_state_has_fund_overview_report(self):
        """Test that initial state includes fund_overview_report."""
        from tradingagents.graph.propagation import Propagator
        
        propagator = Propagator()
        state = propagator.create_initial_state("AAPL", "2026-01-01")
        
        assert "fund_overview_report" in state
        assert state["fund_overview_report"] == ""


class TestTradingGraphFundTools:
    """Test that TradingAgentsGraph has fund tool nodes."""

    def test_create_tool_nodes_has_fund_node(self):
        """Test that _create_tool_nodes returns a 'fund' tool node."""
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        graph = TradingAgentsGraph(selected_analysts=["market"])
        
        tool_nodes = graph._create_tool_nodes()
        
        assert "fund" in tool_nodes


class TestYFinanceFundFunctions:
    """Unit tests for yfinance fund functions (mocked)."""

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_detect_asset_type_stock(self, mock_ticker):
        """Test detect_asset_type for stock."""
        mock_instance = MagicMock()
        mock_instance.fast_info.quote_type = 'EQUITY'
        mock_ticker.return_value = mock_instance
        
        from tradingagents.dataflows.y_finance import detect_asset_type
        
        result = detect_asset_type("AAPL")
        
        assert result == "STOCK"
        mock_ticker.assert_called_once_with("AAPL")

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_detect_asset_type_etf(self, mock_ticker):
        """Test detect_asset_type for ETF."""
        mock_instance = MagicMock()
        mock_instance.fast_info.quote_type = 'ETF'
        mock_ticker.return_value = mock_instance
        
        from tradingagents.dataflows.y_finance import detect_asset_type
        
        result = detect_asset_type("SPY")
        
        assert result == "ETF"

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_detect_asset_type_mutualfund(self, mock_ticker):
        """Test detect_asset_type for mutual fund."""
        mock_instance = MagicMock()
        mock_instance.fast_info.quote_type = 'MUTUALFUND'
        mock_ticker.return_value = mock_instance
        
        from tradingagents.dataflows.y_finance import detect_asset_type
        
        result = detect_asset_type("VFINX")
        
        assert result == "MUTUAL_FUND"

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_detect_asset_type_fallback_info(self, mock_ticker):
        """Test detect_asset_type fallback to info when fast_info fails."""
        mock_instance = MagicMock()
        type(mock_instance).fast_info = property(lambda self: self._raise_exception())
        mock_instance._raise_exception = MagicMock(side_effect=Exception("fast_info failed"))
        mock_instance.info = {'quoteType': 'ETF'}
        mock_ticker.return_value = mock_instance
        
        from tradingagents.dataflows.y_finance import detect_asset_type
        
        result = detect_asset_type("SPY")
        
        assert result == "ETF"

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_detect_asset_type_fund_family_fallback(self, mock_ticker):
        """Test detect_asset_type using fundFamily fallback."""
        mock_instance = MagicMock()
        type(mock_instance).fast_info = property(lambda self: self._raise_exception())
        mock_instance._raise_exception = MagicMock(side_effect=Exception("fast_info failed"))
        mock_instance.info = {'quoteType': 'UNKNOWN', 'fundFamily': 'Vanguard'}
        mock_ticker.return_value = mock_instance
        
        from tradingagents.dataflows.y_finance import detect_asset_type
        
        result = detect_asset_type("VOO")
        
        assert result == "FUND"

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_detect_asset_type_exception_handling(self, mock_ticker):
        """Test that detect_asset_type handles exceptions gracefully."""
        mock_ticker.side_effect = Exception("Connection error")
        
        from tradingagents.dataflows.y_finance import detect_asset_type
        
        result = detect_asset_type("INVALID")
        
        assert "UNKNOWN" in result
        assert "error" in result.lower()


class TestBackwardCompatibility:
    """Test that existing stock functionality is not broken."""

    def test_stock_analyst_still_importable(self):
        """Test that existing stock analysts can still be imported."""
        from tradingagents.agents import (
            create_fundamentals_analyst,
            create_market_analyst,
            create_news_analyst,
            create_social_media_analyst,
        )
        
        assert create_fundamentals_analyst is not None
        assert create_market_analyst is not None
        assert create_news_analyst is not None
        assert create_social_media_analyst is not None

    def test_stock_tools_still_importable(self):
        """Test that existing stock tools can still be imported."""
        from tradingagents.agents.utils.agent_utils import (
            get_stock_data,
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
            get_news,
            get_global_news,
            get_insider_transactions,
        )
        
        assert get_stock_data is not None
        assert get_fundamentals is not None
        assert get_balance_sheet is not None
        assert get_cashflow is not None
        assert get_income_statement is not None
        assert get_news is not None
        assert get_global_news is not None
        assert get_insider_transactions is not None

    def test_interface_stock_methods_preserved(self):
        """Test that existing stock methods are still in interface."""
        from tradingagents.dataflows.interface import VENDOR_METHODS, TOOLS_CATEGORIES
        
        stock_methods = [
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
        
        for method in stock_methods:
            assert method in VENDOR_METHODS, f"Stock method {method} removed from VENDOR_METHODS"

    def test_agent_state_stock_fields_preserved(self):
        """Test that existing stock fields are still in AgentState."""
        from tradingagents.agents.utils.agent_states import AgentState
        
        stock_fields = [
            "company_of_interest",
            "trade_date",
            "market_report",
            "fundamentals_report",
            "sentiment_report",
            "news_report",
        ]
        
        for field in stock_fields:
            assert field in AgentState.__annotations__, f"Stock field {field} removed from AgentState"
