import os

# ⚠️ 第一步：在导入 yfinance 之前，强制注入全局代理环境变量
PROXY = "http://127.0.0.1:7890"  # 请确保这是您真实的代理端口
os.environ["http_proxy"] = PROXY
os.environ["https_proxy"] = PROXY
os.environ["HTTP_PROXY"] = PROXY
os.environ["HTTPS_PROXY"] = PROXY

# 注入完成后，再导入 yfinance
import yfinance as yf

def test_ultimate_proxy():
    ticker_symbol = "AAPL"
    print(f"尝试通过代码级环境变量强制代理 {PROXY} 请求: {ticker_symbol} ...")
    
    try:
        # 直接按照最普通的写法即可，底层会自动走代理
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1d")
        
        if hist.empty:
            print("⚠️ 连接没报错，但没拿到数据。")
        else:
            print("\n✅ 代理生效，成功绕过风控拿到数据！")
            print(hist[['Open', 'High', 'Low', 'Close', 'Volume']])
            
    except Exception as e:
        print(f"\n❌ 依然失败: {e}")

if __name__ == "__main__":
    test_ultimate_proxy()