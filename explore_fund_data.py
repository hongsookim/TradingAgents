# Temporary exploration script for fund data
import os
import tempfile
import pandas as pd

# Create temp cache dir
temp_cache = tempfile.mkdtemp()
os.environ['YF_CACHE_DIR'] = temp_cache

# Set proxy
PROXY = "http://127.0.0.1:7890"
os.environ["http_proxy"] = PROXY
os.environ["https_proxy"] = PROXY
os.environ["HTTP_PROXY"] = PROXY
os.environ["HTTPS_PROXY"] = PROXY

import yfinance as yf

def explore_ticker(symbol, expected_type):
    print(f"\n{'='*60}")
    print(f"Exploring: {symbol} (Expected: {expected_type})")
    print('='*60)
    
    ticker = yf.Ticker(symbol)
    
    # 1. fast_info - reliable, no cache issues
    print("\n--- fast_info (reliable) ---")
    try:
        fast = ticker.fast_info
        print(f"  quote_type: {fast.quote_type}")
        print(f"  currency: {fast.currency}")
        print(f"  exchange: {fast.exchange}")
        print(f"  last_price: {fast.last_price}")
        print(f"  year_change: {fast.year_change}")
        print(f"  year_high: {fast.year_high}")
        print(f"  year_low: {fast.year_low}")
        print(f"  fifty_day_average: {fast.fifty_day_average}")
        print(f"  two_hundred_day_average: {fast.two_hundred_day_average}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 2. History data (for NAV calculation)
    print("\n--- History Data (NAV Proxy) ---")
    try:
        hist = ticker.history(period="1mo")
        if not hist.empty:
            print(f"  Got {len(hist)} days of data")
            print(f"  Columns: {list(hist.columns)}")
            if 'Close' in hist.columns:
                # Calculate drawdown
                rolling_max = hist['Close'].cummax()
                drawdown = (hist['Close'] - rolling_max) / rolling_max
                max_drawdown = drawdown.min()
                print(f"  Max drawdown (1mo): {max_drawdown:.2%}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 3. Try info with better error handling
    print("\n--- Info Fields ---")
    try:
        # Try to access info directly
        info = ticker.info
        if info:
            fund_relevant_keys = [
                'quoteType', 'fundFamily', 'fundInceptionDate',
                'expenseRatio', 'annualReportExpenseRatio',
                'beta', 'beta3Year', 
                'sharpeRatio', 'sharpeRatio3Year', 'sharpeRatio5Year',
                'alpha', 'alpha3Year',
                'standardDeviation', 'standardDeviation3Year',
                'treynorRatio',
                'maxDrawdown',
                'ytdReturn', 'threeYearAverageReturn', 'fiveYearAverageReturn',
                'totalAssets', 'netAssets',
                'category', 'investmentStrategy', 'fundObjective',
                'longName', 'shortName',
                'legalType',
                'managerName', 'managementInfo',
            ]
            
            found = []
            for key in fund_relevant_keys:
                if key in info and info[key] is not None:
                    print(f"  {key}: {info[key]}")
                    found.append(key)
            
            if not found:
                print("  No fund-specific info found. All keys:")
                for key in sorted(info.keys()):
                    print(f"    {key}: {info[key]}")
        else:
            print("  No info available")
    except Exception as e:
        print(f"  Could not get full info: {e}")
        # Alternative: try to get from other sources
        
    # 4. Holdings
    print("\n--- Holdings ---")
    try:
        # Try holdings
        if hasattr(ticker, 'holdings'):
            holdings = ticker.holdings
            if holdings is not None and not holdings.empty:
                print(f"  Found {len(holdings)} holdings")
                print(holdings.head(10))
            else:
                print("  No holdings data")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 5. Major holders / Institutional holders
    print("\n--- Major/Institutional Holders ---")
    try:
        if hasattr(ticker, 'major_holders'):
            major = ticker.major_holders
            if major is not None:
                print(f"  Major holders: {major}")
    except Exception as e:
        print(f"  Major holders error: {e}")
    
    try:
        if hasattr(ticker, 'institutional_holders'):
            inst = ticker.institutional_holders
            if inst is not None and not inst.empty:
                print(f"  Institutional holders (first 5):")
                print(inst.head())
    except Exception as e:
        print(f"  Institutional holders error: {e}")
    
    # 6. Try to get sector weights/holdings via other means
    print("\n--- Sector/Industry Exposure ---")
    try:
        # Some ETFs have sector info in info dict
        info = ticker.info
        if info:
            for key in info.keys():
                if 'sector' in key.lower() or 'weight' in key.lower() or 'hold' in key.lower():
                    print(f"  {key}: {info[key]}")
    except:
        pass

# Test various asset types
test_cases = [
    ("AAPL", "Stock"),
    ("SPY", "ETF - S&P 500"),
    ("QQQ", "ETF - Nasdaq 100"),
    ("VOO", "ETF - Vanguard S&P 500"),
    ("VFINX", "Mutual Fund - Vanguard 500 Index"),
    ("VTIP", "ETF - TIPS Bond"),
]

print("="*60)
print("YFinance Fund Data Exploration")
print("="*60)

for symbol, expected_type in test_cases:
    explore_ticker(symbol, expected_type)

# Test asset type detection
print("\n" + "="*60)
print("Asset Type Detection Summary")
print("="*60)

def detect_asset_type(symbol):
    ticker = yf.Ticker(symbol)
    try:
        fast = ticker.fast_info
        quote_type = fast.quote_type
        
        if quote_type == 'ETF':
            return 'ETF'
        elif quote_type == 'MUTUALFUND':
            return 'MUTUAL_FUND'
        elif quote_type in ['EQUITY', 'STOCK']:
            return 'STOCK'
        else:
            # Fallback detection
            try:
                info = ticker.info
                if info and info.get('fundFamily'):
                    return 'FUND'
                if info and info.get('expenseRatio') is not None:
                    return 'POSSIBLE_FUND'
            except:
                pass
            return quote_type
    except Exception as e:
        return f"UNKNOWN (error: {e})"

for symbol, expected_type in test_cases:
    detected = detect_asset_type(symbol)
    status = "✓" if detected in ['ETF', 'MUTUAL_FUND', 'STOCK'] or expected_type in detected else "?"
    print(f"  {status} {symbol}: Expected '{expected_type}', Detected '{detected}'")

print("\n" + "="*60)
print("Key Findings Summary")
print("="*60)
print("""
1. Asset Type Detection:
   - Use ticker.fast_info.quote_type (most reliable, no cache issues)
   - Values: 'ETF', 'MUTUALFUND', 'EQUITY'

2. Data Available via fast_info:
   - quote_type, currency, exchange
   - last_price, year_change, year_high/low
   - moving averages (50-day, 200-day)
   - volume data

3. Historical Data (for NAV proxy):
   - ticker.history() works for both stocks and ETFs
   - Can calculate max drawdown from Close prices

4. Fund-Specific Data (if available in info):
   - expenseRatio, fundFamily, fundInceptionDate
   - beta3Year, sharpeRatio3Year, alpha3Year
   - maxDrawdown, ytdReturn, threeYearAverageReturn
   - totalAssets, category, investmentStrategy

5. Holdings:
   - ticker.holdings - may not work for all ETFs
   - ticker.institutional_holders - institutional ownership

Recommendations:
- Use fast_info for primary detection and basic metrics
- Use history() for NAV/price analysis and drawdown calculation
- Try info for fund-specific metrics, with graceful fallbacks
- Add defensive try-except for all data access
""")
