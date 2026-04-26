"""
Integration test for China A-Share market support.
Tests import, configuration, and basic functionality without network calls.
"""

import sys
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PASSED = "PASSED"
FAILED = "FAILED"


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_result(name, result, details=""):
    status = PASSED if result else FAILED
    symbol = "[OK]" if result else "[ERROR]"
    print(f"{symbol} {name}: {status}")
    if details:
        print(f"       Details: {details}")


def test_akshare_import():
    """Test akshare data module imports."""
    print_section("Test 1: AKShare Module Imports")
    
    try:
        from tradingagents.dataflows import akshare_data
        print_result("Import akshare_data module", True)
        
        required_funcs = [
            'get_akshare_stock_data',
            'get_akshare_indicators',
            'get_akshare_fundamentals',
            'get_akshare_news',
            'detect_akshare_asset_type',
            'get_akshare_fund_nav',
            'get_akshare_fund_holdings',
            'get_akshare_fund_manager_info',
            'get_akshare_fund_expense_ratio',
            'get_akshare_fund_risk_metrics',
            'get_akshare_fund_overview',
        ]
        
        all_found = True
        for func in required_funcs:
            if hasattr(akshare_data, func):
                print_result(f"  - {func}", True)
            else:
                print_result(f"  - {func}", False, "Missing function")
                all_found = False
        
        return all_found
    except Exception as e:
        print_result("Import akshare_data module", False, str(e))
        return False


def test_interface_registration():
    """Test akshare registration in interface.py."""
    print_section("Test 2: Interface Registration")
    
    try:
        from tradingagents.dataflows.interface import VENDOR_LIST, VENDOR_METHODS
        
        # Check akshare in vendor list
        if "akshare" in VENDOR_LIST:
            print_result("akshare in VENDOR_LIST", True)
        else:
            print_result("akshare in VENDOR_LIST", False, f"Found: {VENDOR_LIST}")
            return False
        
        # Check core methods have akshare
        core_methods = [
            "get_stock_data",
            "get_indicators",
            "get_fundamentals",
            "get_news",
        ]
        
        all_ok = True
        for method in core_methods:
            if method in VENDOR_METHODS and "akshare" in VENDOR_METHODS[method]:
                print_result(f"  - akshare registered for {method}", True)
            else:
                print_result(f"  - akshare registered for {method}", False)
                all_ok = False
        
        # Check fund methods have akshare
        fund_methods = [
            "detect_asset_type",
            "get_fund_nav",
            "get_fund_holdings",
            "get_fund_overview",
        ]
        
        for method in fund_methods:
            if method in VENDOR_METHODS and "akshare" in VENDOR_METHODS[method]:
                print_result(f"  - akshare registered for {method}", True)
            else:
                print_result(f"  - akshare registered for {method}", False)
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_result("Interface registration test", False, str(e))
        return False


def test_default_config():
    """Test China market configuration in default_config.py."""
    print_section("Test 3: Default Configuration")
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # Check market field
        if "market" in DEFAULT_CONFIG:
            print_result(f"'market' field in config (default: {DEFAULT_CONFIG['market']})", True)
        else:
            print_result("'market' field in config", False)
            return False
        
        # Check china_market section
        if "china_market" in DEFAULT_CONFIG:
            print_result("'china_market' section in config", True)
            china_config = DEFAULT_CONFIG["china_market"]
            
            # Check trading hours
            if "trading_hours" in china_config:
                th = china_config["trading_hours"]
                print_result(f"  - trading_hours: {th['morning_start']}-{th['morning_end']}, {th['afternoon_start']}-{th['afternoon_end']}", True)
            else:
                print_result("  - trading_hours", False)
            
            # Check price limits
            if "price_limit" in china_config:
                pl = china_config["price_limit"]
                print_result(f"  - price_limit: normal={pl['normal']}, st={pl['st']}, star={pl['star']}, chinext={pl['chinext']}", True)
            else:
                print_result("  - price_limit", False)
            
            # Check trading mechanism
            if "trading_mechanism" in china_config:
                tm = china_config["trading_mechanism"]
                print_result(f"  - trading_mechanism: settlement={tm['settlement_cycle']}", True)
            else:
                print_result("  - trading_mechanism", False)
        else:
            print_result("'china_market' section in config", False)
            return False
        
        return True
    except Exception as e:
        print_result("Default config test", False, str(e))
        return False


def test_cli_market_config():
    """Test CLI market type and vendor configuration."""
    print_section("Test 4: CLI Market Configuration")
    
    try:
        from cli.models import MarketType, MARKET_VENDOR_CONFIG
        
        # Check MarketType enum
        if MarketType.US.value == "us" and MarketType.KR.value == "kr" and MarketType.CN.value == "cn":
            print_result("MarketType enum values correct", True)
        else:
            print_result("MarketType enum values", False, f"US={MarketType.US.value}, KR={MarketType.KR.value}, CN={MarketType.CN.value}")
        
        # Check MARKET_VENDOR_CONFIG
        all_ok = True
        for market in ["us", "kr", "cn"]:
            if market in MARKET_VENDOR_CONFIG:
                config = MARKET_VENDOR_CONFIG[market]
                if "description" in config and "data_vendors" in config and "ticker_examples" in config:
                    print_result(f"  - {market} market config complete", True)
                    
                    # Check specific vendor settings
                    if market == "cn":
                        dv = config["data_vendors"]
                        if all(v == "akshare" for k, v in dv.items() if k != "dart_data"):
                            print_result(f"    - CN uses akshare for all data types", True)
                        else:
                            print_result(f"    - CN vendor config", False, f"{dv}")
                            all_ok = False
                    elif market == "us" or market == "kr":
                        dv = config["data_vendors"]
                        if dv.get("core_stock_apis") == "yfinance":
                            print_result(f"    - {market.upper()} uses yfinance (backward compatible)", True)
                        else:
                            print_result(f"    - {market.upper()} vendor config", False)
                            all_ok = False
                else:
                    print_result(f"  - {market} market config", False, "Missing fields")
                    all_ok = False
            else:
                print_result(f"  - {market} market config", False, "Not found")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_result("CLI market config test", False, str(e))
        return False


def test_asset_type_detection():
    """Test akshare asset type detection."""
    print_section("Test 5: Asset Type Detection")
    
    try:
        from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
        
        all_ok = True
        
        # Test Shanghai stocks
        shanghai_stocks = ["600519", "601318", "603288", "688981"]
        for ticker in shanghai_stocks:
            result = detect_akshare_asset_type(ticker)
            if result == "STOCK":
                print_result(f"  - {ticker} -> STOCK", True)
            else:
                print_result(f"  - {ticker} -> STOCK", False, f"Got: {result}")
                all_ok = False
        
        # Test Shenzhen stocks
        shenzhen_stocks = ["000001", "002415", "300750"]
        for ticker in shenzhen_stocks:
            result = detect_akshare_asset_type(ticker)
            if result == "STOCK":
                print_result(f"  - {ticker} -> STOCK", True)
            else:
                print_result(f"  - {ticker} -> STOCK", False, f"Got: {result}")
                all_ok = False
        
        # Test ETFs
        etfs = ["510300", "510500", "159915"]
        for ticker in etfs:
            result = detect_akshare_asset_type(ticker)
            if result == "ETF":
                print_result(f"  - {ticker} -> ETF", True)
            else:
                print_result(f"  - {ticker} -> ETF", False, f"Got: {result}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_result("Asset type detection test", False, str(e))
        return False


def test_backward_compatibility():
    """Test backward compatibility with US/KR markets."""
    print_section("Test 6: Backward Compatibility")
    
    try:
        all_ok = True
        
        # Test that existing imports still work
        from tradingagents.dataflows.interface import VENDOR_METHODS
        
        # Check that yfinance is still registered for all core methods
        core_methods = [
            "get_stock_data", "get_indicators", "get_fundamentals",
            "get_balance_sheet", "get_cashflow", "get_income_statement",
            "get_news", "get_global_news", "get_insider_transactions",
        ]
        
        for method in core_methods:
            if method in VENDOR_METHODS and "yfinance" in VENDOR_METHODS[method]:
                print_result(f"  - yfinance still registered for {method}", True)
            else:
                print_result(f"  - yfinance still registered for {method}", False)
                all_ok = False
        
        # Check that default config still uses yfinance
        from tradingagents.default_config import DEFAULT_CONFIG
        
        expected_vendors = {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "yfinance",
            "news_data": "yfinance",
            "dart_data": "opendart",
            "fund_data": "yfinance",
        }
        
        for key, expected in expected_vendors.items():
            actual = DEFAULT_CONFIG["data_vendors"].get(key)
            if actual == expected:
                print_result(f"  - data_vendors['{key}'] = {actual}", True)
            else:
                print_result(f"  - data_vendors['{key}']", False, f"Expected {expected}, got {actual}")
                all_ok = False
        
        # Check agent tools still importable
        from tradingagents.agents.utils.agent_utils import (
            get_stock_data, get_indicators, get_fundamentals, get_news,
            detect_asset_type, get_fund_nav, get_fund_overview,
        )
        
        tools = [get_stock_data, get_indicators, get_fundamentals, get_news,
                 detect_asset_type, get_fund_nav, get_fund_overview]
        
        for tool in tools:
            if tool is not None:
                print_result(f"  - {tool.__name__} importable", True)
            else:
                print_result(f"  - tool import", False)
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_result("Backward compatibility test", False, str(e))
        return False


def test_defensive_programming():
    """Test defensive programming (error handling)."""
    print_section("Test 7: Defensive Programming")
    
    try:
        from tradingagents.dataflows.akshare_data import (
            get_akshare_stock_data,
            get_akshare_fund_nav,
            get_akshare_indicators,
        )
        
        all_ok = True
        
        # Test that functions handle errors gracefully (no exceptions)
        try:
            result = get_akshare_stock_data("INVALID_CODE", "2026-01-01", "2026-01-31")
            if isinstance(result, str) and ("error" in result.lower() or "failed" in result.lower() or "获取" in result):
                print_result("  - get_akshare_stock_data handles invalid input gracefully", True)
            else:
                print_result("  - get_akshare_stock_data error handling", True, f"Returned: {result[:100]}...")
        except Exception as e:
            print_result("  - get_akshare_stock_data error handling", False, f"Threw exception: {e}")
            all_ok = False
        
        try:
            result = get_akshare_fund_nav("INVALID_FUND", period="1y")
            if isinstance(result, str):
                print_result("  - get_akshare_fund_nav handles invalid input gracefully", True)
            else:
                print_result("  - get_akshare_fund_nav error handling", True)
        except Exception as e:
            print_result("  - get_akshare_fund_nav error handling", False, f"Threw exception: {e}")
            all_ok = False
        
        # Test invalid indicator
        try:
            result = get_akshare_indicators("600519", "INVALID_INDICATOR", "2026-01-31", 30)
            if isinstance(result, str):
                print_result("  - get_akshare_indicators handles invalid indicator", True)
            else:
                print_result("  - get_akshare_indicators error handling", True)
        except Exception as e:
            print_result("  - get_akshare_indicators error handling", False, f"Threw exception: {e}")
            all_ok = False
        
        return all_ok
    except Exception as e:
        print_result("Defensive programming test", False, str(e))
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("  China A-Share Support Integration Tests")
    print("="*60)
    
    results = {}
    
    results["akshare_import"] = test_akshare_import()
    results["interface_registration"] = test_interface_registration()
    results["default_config"] = test_default_config()
    results["cli_market_config"] = test_cli_market_config()
    results["asset_type_detection"] = test_asset_type_detection()
    results["backward_compatibility"] = test_backward_compatibility()
    results["defensive_programming"] = test_defensive_programming()
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n  Passed: {passed}/{total}")
    print(f"  Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n  [SUCCESS] All tests passed!")
        return True
    else:
        print("\n  [FAILED] Some tests failed:")
        for name, result in results.items():
            if not result:
                print(f"    - {name}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
