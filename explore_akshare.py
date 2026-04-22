#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Explore akshare capabilities for A-share data."""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def explore_akshare():
    """Explore akshare functions for A-share data."""
    import akshare as ak
    
    print("=" * 60)
    print("Exploring Akshare for A-Share Data")
    print("=" * 60)
    
    # Test 1: Stock list
    print("\n1. Testing stock list...")
    try:
        df = ak.stock_info_a_code_name()
        print(f"   Total A-share stocks: {len(df)}")
        print(f"   Sample: {df.head(3).to_dict('records')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Daily stock data
    print("\n2. Testing daily stock data (600519 = Kweichow Moutai)...")
    try:
        df = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date="20260101", end_date="20260422", adjust="qfq")
        print(f"   Data points: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Latest: {df.tail(1).to_dict('records')[0]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Fund NAV data
    print("\n3. Testing fund NAV data (110022 = E Fund Consumption)...")
    try:
        df = ak.fund_nav_open_sina(symbol="110022")
        print(f"   NAV data points: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Latest 3: {df.tail(3).to_dict('records')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Fund info
    print("\n4. Testing fund info...")
    try:
        df = ak.fund_overview_em(symbol="110022")
        print(f"   Fund info: {df.to_dict('records')[0] if not df.empty else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Fund manager info
    print("\n5. Testing fund manager info...")
    try:
        df = ak.fund_manager_name(symbol="110022")
        print(f"   Manager info: {df.to_dict('records') if not df.empty else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Stock fundamentals
    print("\n6. Testing stock fundamentals...")
    try:
        df = ak.stock_individual_info_em(symbol="600519")
        print(f"   Stock info: {df.to_dict('records') if not df.empty else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 7: Balance sheet
    print("\n7. Testing balance sheet...")
    try:
        df = ak.stock_financial_analysis_indicator(symbol="600519")
        print(f"   Balance sheet columns: {list(df.columns)[:10]}")
        print(f"   Latest row: {df.head(1).to_dict('records')[0] if not df.empty else 'No data'}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 8: News
    print("\n8. Testing news data...")
    try:
        df = ak.stock_news_em(symbol="600519")
        print(f"   News count: {len(df)}")
        print(f"   Latest 2: {df.head(2).to_dict('records')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Exploration complete!")
    print("=" * 60)

if __name__ == "__main__":
    explore_akshare()
