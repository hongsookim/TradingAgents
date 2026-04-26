#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Explore akshare fund functions."""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def explore_fund_functions():
    """Explore akshare fund functions."""
    import akshare as ak
    
    print("=" * 60)
    print("Exploring Akshare Fund Functions")
    print("=" * 60)
    
    # List all fund-related functions
    print("\n1. Fund-related functions in akshare:")
    fund_funcs = [f for f in dir(ak) if 'fund' in f.lower()]
    for f in sorted(fund_funcs):
        print(f"   - {f}")
    
    # Test fund net value
    print("\n2. Testing fund NAV functions...")
    
    # Try different NAV functions
    nav_funcs = [
        'fund_open_fund_info_em',
        'fund_em_open_fund_info',
        'fund_net_value',
        'fund_nav',
    ]
    
    for func_name in nav_funcs:
        if hasattr(ak, func_name):
            try:
                print(f"\n   Testing {func_name}...")
                func = getattr(ak, func_name)
                if func_name in ['fund_open_fund_info_em', 'fund_em_open_fund_info']:
                    df = func(symbol="110022", indicator="单位净值走势")
                else:
                    df = func("110022")
                print(f"   Success! Shape: {df.shape}")
                print(f"   Columns: {list(df.columns)}")
                if not df.empty:
                    print(f"   Latest: {df.head(1).to_dict('records')[0]}")
            except Exception as e:
                print(f"   Error: {e}")
    
    # Test fund holdings
    print("\n3. Testing fund holdings...")
    holding_funcs = [
        'fund_portfolio_hold_em',
        'fund_holdings',
        'fund_stock_holdings',
    ]
    for func_name in holding_funcs:
        if hasattr(ak, func_name):
            try:
                print(f"\n   Testing {func_name}...")
                func = getattr(ak, func_name)
                df = func(date="20260331")
                print(f"   Success! Shape: {df.shape}")
                if not df.empty:
                    print(f"   Sample: {df.head(2).to_dict('records')}")
            except Exception as e:
                print(f"   Error: {e}")
    
    # Test fund manager
    print("\n4. Testing fund manager info...")
    manager_funcs = [
        'fund_manager_em',
        'fund_personal_info_em',
    ]
    for func_name in manager_funcs:
        if hasattr(ak, func_name):
            try:
                print(f"\n   Testing {func_name}...")
                func = getattr(ak, func_name)
                df = func()
                print(f"   Success! Shape: {df.shape}")
                if not df.empty:
                    print(f"   Columns: {list(df.columns)}")
                    print(f"   Sample: {df.head(1).to_dict('records')[0]}")
            except Exception as e:
                print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    explore_fund_functions()
