"""
Quick test for detect_akshare_asset_type function.
"""

import sys
import io

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_detect_asset_type():
    """Test the detect_akshare_asset_type function."""
    from tradingagents.dataflows.akshare_data import detect_akshare_asset_type
    
    print("\n" + "="*60)
    print("  Testing detect_akshare_asset_type")
    print("="*60)
    
    all_passed = True
    
    # Test cases
    test_cases = [
        # Stocks
        ("600519", "STOCK", "贵州茅台 - 上海主板"),
        ("601318", "STOCK", "中国平安 - 上海主板"),
        ("603288", "STOCK", "海天味业 - 上海主板"),
        ("688981", "STOCK", "中芯国际 - 科创板"),
        ("000001", "STOCK", "平安银行 - 深圳主板"),
        ("002415", "STOCK", "海康威视 - 中小板"),
        ("300750", "STOCK", "宁德时代 - 创业板"),
        
        # ETFs
        ("510300", "ETF", "沪深300 ETF - 上海"),
        ("510500", "ETF", "中证500 ETF - 上海"),
        ("512880", "ETF", "证券ETF - 上海"),
        ("159915", "ETF", "创业板ETF - 深圳"),
        
        # LOFs
        ("161725", "LOF", "招商中证白酒指数 LOF"),
        ("161005", "LOF", "富国天惠成长 LOF"),
        
        # Mutual Funds (open-end funds)
        ("110022", "MUTUAL_FUND", "易方达消费行业 - 场外基金"),
        ("000001", "STOCK", "平安银行 (注意: 000001 是股票代码)"),
        ("000011", "MUTUAL_FUND", "华夏大盘精选 - 场外基金"),
        ("501018", "MUTUAL_FUND", "南方原油 - 基金"),
        ("180012", "MUTUAL_FUND", "银华富裕主题 - 基金"),
    ]
    
    print("\nTest Results:")
    print("-"*60)
    
    for code, expected, description in test_cases:
        result = detect_akshare_asset_type(code)
        
        # For 000001, it's a stock code
        if code == "000001":
            expected = "STOCK"
        
        passed = result == expected
        
        if passed:
            status = "[OK]"
        else:
            status = "[FAIL]"
            all_passed = False
        
        print(f"{status} {code} -> {result:12} (expected: {expected:12}) - {description}")
    
    print("-"*60)
    
    if all_passed:
        print("\n[SUCCESS] All detect_akshare_asset_type tests passed!")
    else:
        print("\n[FAILED] Some tests failed!")
    
    return all_passed


if __name__ == "__main__":
    test_detect_asset_type()
