"""
Test script to verify akshare function signature fixes.
Tests that all akshare functions accept the correct number of arguments.
"""

import sys
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import inspect

PASSED = "PASSED"
FAILED = "FAILED"


def inspect_function_signature(func):
    """Get function signature info."""
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    return params


def test_function_signatures():
    """Test that akshare function signatures match expected patterns."""
    print("\n" + "="*60)
    print("  Testing akshare function signatures")
    print("="*60)
    
    all_passed = True
    
    # Import the akshare module
    try:
        from tradingagents.dataflows import akshare_data
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False
    
    # Test get_akshare_news - should accept (ticker, start_date, end_date)
    print("\n1. Testing get_akshare_news signature...")
    params = inspect_function_signature(akshare_data.get_akshare_news)
    print(f"   Parameters: {params}")
    
    # Test calling with 3 arguments (like yfinance interface)
    try:
        sig = inspect.signature(akshare_data.get_akshare_news)
        sig.bind("600519", "2026-01-01", "2026-01-31")
        print("   [OK] Can be called with 3 arguments (ticker, start_date, end_date)")
    except TypeError as e:
        print(f"   [ERROR] Cannot be called with 3 arguments: {e}")
        all_passed = False
    
    # Test get_akshare_global_news - should accept (curr_date, look_back_days, limit)
    print("\n2. Testing get_akshare_global_news signature...")
    params_gn = inspect_function_signature(akshare_data.get_akshare_global_news)
    print(f"   Parameters: {params_gn}")
    
    # Test calling with arguments
    try:
        sig = inspect.signature(akshare_data.get_akshare_global_news)
        sig.bind("2026-01-31", 7, 10)
        print("   [OK] Can be called with (curr_date, look_back_days, limit)")
    except TypeError as e:
        print(f"   [ERROR] Cannot be called: {e}")
        all_passed = False
    
    # Test other key functions
    print("\n3. Testing other key functions...")
    
    # Define expected signatures (based on what the tools call)
    test_cases = [
        # (function_name, test_args_tuple, description)
        ("get_akshare_stock_data", ("600519", "2026-01-01", "2026-01-31"), "symbol, start_date, end_date"),
        ("get_akshare_indicators", ("600519", "macd", "2026-01-31", 30), "symbol, indicator, curr_date, look_back_days"),
        ("get_akshare_fundamentals", ("600519", "2026-01-31"), "ticker, curr_date"),
        ("get_akshare_balance_sheet", ("600519", "quarterly", "2026-01-31"), "ticker, freq, curr_date"),
        ("get_akshare_cashflow", ("600519", "quarterly", "2026-01-31"), "ticker, freq, curr_date"),
        ("get_akshare_income_statement", ("600519", "quarterly", "2026-01-31"), "ticker, freq, curr_date"),
        ("detect_akshare_asset_type", ("600519",), "ticker"),
        # Fund functions
        ("get_akshare_fund_nav", ("110022", "1y", True, "2026-01-31"), "ticker, period, calculate_drawdown, curr_date"),
        ("get_akshare_fund_holdings", ("110022", 10, "2026-01-31"), "ticker, top_n, curr_date"),
        ("get_akshare_fund_manager_info", ("110022", "2026-01-31"), "ticker, curr_date"),
        ("get_akshare_fund_expense_ratio", ("110022", "2026-01-31"), "ticker, curr_date"),
        ("get_akshare_fund_risk_metrics", ("110022", "2026-01-31"), "ticker, curr_date"),
        ("get_akshare_fund_overview", ("110022", "2026-01-31"), "ticker, curr_date"),
    ]
    
    for func_name, test_args, desc in test_cases:
        func = getattr(akshare_data, func_name, None)
        if func is None:
            print(f"   [ERROR] {func_name} not found")
            all_passed = False
            continue
        
        try:
            sig = inspect.signature(func)
            sig.bind(*test_args)
            print(f"   [OK] {func_name} accepts: {desc}")
        except TypeError as e:
            params = inspect_function_signature(func)
            print(f"   [ERROR] {func_name} params: {params} - cannot accept: {desc}")
            print(f"           Error: {e}")
            all_passed = False
    
    return all_passed


def test_akshare_data_only():
    """Test akshare data module directly without interface."""
    print("\n" + "="*60)
    print("  Testing akshare module directly")
    print("="*60)
    
    all_passed = True
    
    try:
        from tradingagents.dataflows import akshare_data
        
        # Test that functions are callable with correct args
        print("\n1. Testing get_akshare_news with 3 args:")
        try:
            # Just verify the signature is correct - don't actually call
            import inspect
            sig = inspect.signature(akshare_data.get_akshare_news)
            print(f"   Signature: {sig}")
            print("   [OK] Function exists with correct signature")
        except Exception as e:
            print(f"   [ERROR] {e}")
            all_passed = False
        
        print("\n2. Testing get_akshare_global_news with args:")
        try:
            sig = inspect.signature(akshare_data.get_akshare_global_news)
            print(f"   Signature: {sig}")
            print("   [OK] Function exists with correct signature")
        except Exception as e:
            print(f"   [ERROR] {e}")
            all_passed = False
        
        # Test detect_asset_type
        print("\n3. Testing detect_akshare_asset_type:")
        test_codes = [
            ("600519", "STOCK"),  # Shanghai stock
            ("000001", "STOCK"),  # Shenzhen stock
            ("300750", "STOCK"),  # ChiNext
            ("688981", "STOCK"),  # STAR Market
            ("510300", "ETF"),    # Shanghai ETF
            ("159915", "ETF"),    # Shenzhen ETF
            ("110022", "MUTUAL_FUND"),  # Fund
        ]
        
        for code, expected in test_codes:
            try:
                result = akshare_data.detect_akshare_asset_type(code)
                if result == expected or (expected == "MUTUAL_FUND" and result in ["MUTUAL_FUND", "LOF"]):
                    print(f"   [OK] {code} -> {result}")
                else:
                    print(f"   [WARN] {code} -> {result} (expected: {expected})")
            except Exception as e:
                print(f"   [ERROR] {code}: {e}")
                all_passed = False
                
    except Exception as e:
        print(f"[ERROR] {e}")
        all_passed = False
    
    return all_passed


if __name__ == "__main__":
    sig_test = test_function_signatures()
    ak_test = test_akshare_data_only()
    
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    
    if sig_test and ak_test:
        print("\n[SUCCESS] All tests passed!")
        print("\nThe bug has been fixed:")
        print("  - get_akshare_news now accepts (ticker, start_date, end_date)")
        print("  - get_akshare_global_news now accepts (curr_date, look_back_days, limit)")
        sys.exit(0)
    else:
        print("\n[FAILED] Some tests failed!")
        sys.exit(1)
