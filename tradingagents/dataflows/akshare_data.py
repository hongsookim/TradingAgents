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

"""
Akshare data provider for China A-share market.

This module provides data retrieval functions for:
- A-share stocks (Shanghai/Shenzhen exchanges)
- A-share mutual funds (公募基金)
- A-share ETFs

Using akshare library as the data source.
"""

from typing import Annotated
from datetime import datetime, date, timedelta
import pandas as pd


def _get_akshare():
    """Lazy import of akshare to avoid dependency issues."""
    try:
        import akshare as ak
        return ak
    except ImportError:
        raise ImportError("akshare package required: pip install akshare")


def _format_date(dt_str: str) -> str:
    """Convert date string to YYYYMMDD format for akshare."""
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        return dt.strftime("%Y%m%d")
    except ValueError:
        return dt_str


def _parse_date_to_iso(dt_obj) -> str:
    """Convert various date types to ISO format string."""
    if isinstance(dt_obj, str):
        return dt_obj
    if isinstance(dt_obj, date):
        return dt_obj.strftime("%Y-%m-%d")
    if hasattr(dt_obj, 'strftime'):
        return dt_obj.strftime("%Y-%m-%d")
    return str(dt_obj)


def _df_to_string(df: pd.DataFrame, max_rows: int = 50) -> str:
    """Convert DataFrame to string with proper encoding handling."""
    if df is None or df.empty:
        return "No data available"
    
    df_str = df.to_string(index=False)
    
    try:
        df_str = df_str.encode('utf-8', errors='ignore').decode('utf-8')
    except Exception:
        pass
    
    return df_str


def get_akshare_stock_data(
    symbol: Annotated[str, "ticker symbol of the A-share company (6-digit code)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Get A-share stock historical data (OHLCV) from akshare.
    
    Args:
        symbol: 6-digit A-share stock code (e.g., '600519' for Kweichow Moutai)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Formatted string with stock price data
    """
    try:
        ak = _get_akshare()
        
        start_ak = _format_date(start_date)
        end_ak = _format_date(end_date)
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_ak,
            end_date=end_ak,
            adjust="qfq"
        )
        
        if df is None or df.empty:
            return f"No A-share data found for symbol '{symbol}' between {start_date} and {end_date}"
        
        column_mapping = {
            '日期': 'Date',
            '股票代码': 'Ticker',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
            '成交额': 'Amount',
            '振幅': 'Amplitude',
            '涨跌幅': 'Change_Pct',
            '涨跌额': 'Change_Amt',
            '换手率': 'Turnover',
        }
        
        df = df.rename(columns=column_mapping)
        
        if 'Date' in df.columns:
            df['Date'] = df['Date'].apply(_parse_date_to_iso)
        
        numeric_cols = ['Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 
                        'Amplitude', 'Change_Pct', 'Change_Amt', 'Turnover']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'Open' in df.columns:
            df['Open'] = df['Open'].round(2)
        if 'Close' in df.columns:
            df['Close'] = df['Close'].round(2)
        if 'High' in df.columns:
            df['High'] = df['High'].round(2)
        if 'Low' in df.columns:
            df['Low'] = df['Low'].round(2)
        
        lines = []
        header = f"# A-Share Stock Data for {symbol} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(df)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: Akshare (东方财富)\n\n"
        lines.append(header)
        
        lines.append(_df_to_string(df))
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share stock data for {symbol}: {str(e)}"


def get_akshare_indicators(
    symbol: Annotated[str, "ticker symbol of the A-share company"],
    indicator: Annotated[str, "technical indicator to get"],
    curr_date: Annotated[str, "current trading date"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    Calculate technical indicators for A-share stocks.
    
    This uses stockstats library similar to yfinance implementation.
    
    Args:
        symbol: 6-digit A-share stock code
        indicator: Technical indicator name
        curr_date: Current date in YYYY-MM-DD format
        look_back_days: Number of days to look back
    
    Returns:
        Formatted string with indicator values
    """
    try:
        from .stockstats_utils import StockstatsUtils
        
        indicator_description = {
            "close_50_sma": "50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance.",
            "close_200_sma": "200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend.",
            "close_10_ema": "10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum.",
            "macd": "MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence.",
            "macds": "MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line.",
            "macdh": "MACD Histogram: Shows the gap between MACD and its signal. Usage: Visualize momentum strength.",
            "rsi": "RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds.",
            "boll": "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands.",
            "boll_ub": "Bollinger Upper Band: Typically 2 standard deviations above middle line.",
            "boll_lb": "Bollinger Lower Band: Typically 2 standard deviations below middle line.",
            "atr": "ATR: Averages true range to measure volatility. Usage: Set stop-loss levels.",
            "vwma": "VWMA: A moving average weighted by volume. Usage: Confirm trends integrating price and volume.",
            "mfi": "MFI: Money Flow Index uses price and volume to measure buying/selling pressure.",
        }
        
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        before = curr_date_dt - timedelta(days=look_back_days)
        start_date = before.strftime("%Y-%m-%d")
        
        ak = _get_akshare()
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=_format_date(start_date),
            end_date=_format_date(curr_date),
            adjust="qfq"
        )
        
        if df is None or df.empty:
            return f"No data available for {symbol} to calculate {indicator}"
        
        column_mapping = {
            '日期': 'Date',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
        }
        df = df.rename(columns=column_mapping)
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'Adj Close' not in df.columns:
            df['Adj Close'] = df['Close']
        
        from stockstats import wrap
        df_stats = wrap(df)
        
        if indicator not in df_stats.columns:
            try:
                df_stats[indicator]
            except Exception:
                return f"Indicator {indicator} is not supported for A-share data."
        
        result_lines = []
        result_lines.append(f"## {indicator} values from {start_date} to {curr_date}:\n")
        
        df_sorted = df_stats.sort_values('Date', ascending=False)
        
        count = 0
        for idx, row in df_sorted.iterrows():
            if count >= look_back_days:
                break
            date_str = _parse_date_to_iso(row['Date'])
            try:
                value = row[indicator]
                if pd.isna(value):
                    result_lines.append(f"{date_str}: N/A")
                else:
                    result_lines.append(f"{date_str}: {value:.4f}")
            except Exception:
                result_lines.append(f"{date_str}: N/A")
            count += 1
        
        result_lines.append("\n")
        result_lines.append(indicator_description.get(indicator, "No description available."))
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error calculating indicator {indicator} for {symbol}: {str(e)}"


def get_akshare_fundamentals(
    ticker: Annotated[str, "ticker symbol of the A-share company"],
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share company fundamentals overview from akshare.
    
    Args:
        ticker: 6-digit A-share stock code
        curr_date: Current date (for compatibility)
    
    Returns:
        Formatted string with fundamentals information
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Company Fundamentals for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: Akshare (东方财富)\n\n"
        lines.append(header)
        
        info_found = False
        
        try:
            df = ak.stock_individual_info_em(symbol=ticker)
            if df is not None and not df.empty:
                info_dict = {}
                for _, row in df.iterrows():
                    key = row.get('item', row.get('item', ''))
                    value = row.get('value', '')
                    if key and value is not None:
                        info_dict[str(key)] = value
                
                if info_dict:
                    lines.append("## Basic Information:\n")
                    name_translation = {
                        '股票代码': 'Ticker',
                        '股票简称': 'Name',
                        '总股本': 'Total Shares',
                        '流通股': 'Float Shares',
                        '总市值': 'Total Market Cap',
                        '流通市值': 'Float Market Cap',
                        '行业': 'Industry',
                        '上市时间': 'Listing Date',
                        '最新': 'Latest Price',
                    }
                    
                    for key, value in info_dict.items():
                        display_name = name_translation.get(key, key)
                        lines.append(f"{display_name}: {value}")
                    info_found = True
                    lines.append("\n")
        except Exception:
            pass
        
        try:
            df = ak.stock_financial_analysis_indicator(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("## Financial Indicators (Latest Quarter):\n")
                
                if len(df) > 0:
                    latest = df.iloc[0]
                    
                    for col in df.columns[:15]:
                        if col in latest and not pd.isna(latest[col]):
                            lines.append(f"{col}: {latest[col]}")
                    
                    lines.append("\n")
                    info_found = True
        except Exception:
            pass
        
        if not info_found:
            lines.append("Note: Detailed fundamentals data not available for this stock.\n")
            lines.append("This may be due to API limitations or the stock being newly listed.\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fundamentals for {ticker}: {str(e)}"


def get_akshare_balance_sheet(
    ticker: Annotated[str, "ticker symbol of the A-share company"],
    freq: Annotated[str, "frequency of data"] = "quarterly",
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share balance sheet data from akshare.
    
    Args:
        ticker: 6-digit A-share stock code
        freq: Frequency (annual/quarterly)
        curr_date: Current date
    
    Returns:
        Formatted string with balance sheet data
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Balance Sheet for {ticker} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        try:
            df = ak.stock_financial_analysis_indicator(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("Note: Using financial analysis indicators (balance sheet data integrated).\n\n")
                lines.append(_df_to_string(df.head(10)))
            else:
                lines.append("No balance sheet data available for this stock.\n")
        except Exception as e:
            lines.append(f"Note: Balance sheet data not available via this API. Error: {e}\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share balance sheet for {ticker}: {str(e)}"


def get_akshare_income_statement(
    ticker: Annotated[str, "ticker symbol of the A-share company"],
    freq: Annotated[str, "frequency of data"] = "quarterly",
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share income statement data from akshare.
    
    Args:
        ticker: 6-digit A-share stock code
        freq: Frequency
        curr_date: Current date
    
    Returns:
        Formatted string with income statement data
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Income Statement for {ticker} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        try:
            df = ak.stock_financial_analysis_indicator(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("Note: Using financial analysis indicators.\n\n")
                lines.append(_df_to_string(df.head(10)))
            else:
                lines.append("No income statement data available.\n")
        except Exception as e:
            lines.append(f"Note: Income statement data not available. Error: {e}\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share income statement for {ticker}: {str(e)}"


def get_akshare_cashflow(
    ticker: Annotated[str, "ticker symbol of the A-share company"],
    freq: Annotated[str, "frequency of data"] = "quarterly",
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share cash flow statement data from akshare.
    
    Args:
        ticker: 6-digit A-share stock code
        freq: Frequency
        curr_date: Current date
    
    Returns:
        Formatted string with cash flow data
    """
    return get_akshare_income_statement(ticker, freq, curr_date)


def get_akshare_news(
    ticker: Annotated[str, "ticker symbol of the A-share company"]
) -> str:
    """
    Get A-share stock news from akshare.
    
    Args:
        ticker: 6-digit A-share stock code
    
    Returns:
        Formatted string with news data
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share News for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: Akshare (东方财富)\n\n"
        lines.append(header)
        
        try:
            df = ak.stock_news_em(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("## Recent News:\n")
                
                count = 0
                for _, row in df.iterrows():
                    if count >= 10:
                        break
                    
                    title = row.get('新闻标题', row.get('标题', 'No Title'))
                    content = row.get('新闻内容', row.get('内容', ''))
                    pub_time = row.get('发布时间', row.get('时间', ''))
                    source = row.get('文章来源', row.get('来源', ''))
                    url = row.get('新闻链接', row.get('链接', ''))
                    
                    lines.append(f"### {title}\n")
                    lines.append(f"Published: {pub_time} | Source: {source}\n")
                    if content and str(content).strip():
                        lines.append(f"{str(content)[:500]}...\n" if len(str(content)) > 500 else f"{content}\n")
                    if url:
                        lines.append(f"URL: {url}\n")
                    lines.append("\n")
                    count += 1
            else:
                lines.append("No news data available for this stock.\n")
        except Exception as e:
            lines.append(f"Note: News data not available. Error: {e}\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share news for {ticker}: {str(e)}"


def get_akshare_global_news() -> str:
    """
    Get global/market news from akshare.
    
    Returns:
        Formatted string with global news
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Market News\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        try:
            df = ak.stock_news_global_em()
            if df is not None and not df.empty:
                lines.append("## Global Market News:\n")
                lines.append(_df_to_string(df.head(10)))
            else:
                lines.append("No global news data available.\n")
        except Exception:
            try:
                df = ak.news_latest()
                if df is not None and not df.empty:
                    lines.append("## Latest News:\n")
                    lines.append(_df_to_string(df.head(10)))
                else:
                    lines.append("No news data available.\n")
            except Exception as e:
                lines.append(f"Note: Global news not available. Error: {e}\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving global news: {str(e)}"


def get_akshare_insider_transactions(
    ticker: Annotated[str, "ticker symbol of the A-share company"]
) -> str:
    """
    Get A-share insider transactions from akshare.
    
    Args:
        ticker: 6-digit A-share stock code
    
    Returns:
        Formatted string with insider transactions
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Insider Transactions for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        lines.append("Note: Insider transaction data for A-shares is available through stock announcements.\n")
        lines.append("For detailed insider trading information, please refer to:\n")
        lines.append("- 巨潮资讯网 (http://www.cninfo.com.cn)\n")
        lines.append("- 上交所/深交所 official websites\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share insider transactions for {ticker}: {str(e)}"


def detect_akshare_asset_type(
    ticker: Annotated[str, "ticker symbol to detect asset type"]
) -> str:
    """
    Detect if a ticker represents a Stock, ETF, or Mutual Fund in A-share market.
    
    A-share code rules:
    - 600xxx, 601xxx, 603xxx, 605xxx, 688xxx: Shanghai Stock Exchange
    - 000xxx, 001xxx, 002xxx, 003xxx: Shenzhen Stock Exchange (main board)
    - 300xxx: Shenzhen Stock Exchange (ChiNext)
    - 510xxx, 511xxx, 512xxx, 513xxx, 515xxx, 516xxx, 518xxx, 56xxx: Shanghai ETF
    - 159xxx: Shenzhen ETF
    - 150xxx: Shenzhen Structured Fund
    - 16xxx: LOF Fund
    - 18xxxx: Shanghai Stock Fund
    - 50xxxx: Shanghai封闭式基金
    - 0xxxx (except 000,001,002,003,300): Other funds
    
    Args:
        ticker: Ticker symbol (6-digit code or with .SS/.SZ suffix)
    
    Returns:
        str: One of 'STOCK', 'ETF', 'MUTUAL_FUND', 'LOF', 'UNKNOWN'
    """
    try:
        clean_ticker = ticker.upper().replace('.SS', '').replace('.SZ', '').strip()
        
        if len(clean_ticker) != 6:
            return "UNKNOWN"
        
        if not clean_ticker.isdigit():
            return "UNKNOWN"
        
        code = clean_ticker
        
        if code.startswith('600') or code.startswith('601') or code.startswith('603') or \
           code.startswith('605') or code.startswith('688') or \
           code.startswith('000') or code.startswith('001') or code.startswith('002') or \
           code.startswith('003') or code.startswith('300'):
            return "STOCK"
        
        if code.startswith('510') or code.startswith('511') or code.startswith('512') or \
           code.startswith('513') or code.startswith('515') or code.startswith('516') or \
           code.startswith('518') or code.startswith('56') or code.startswith('159'):
            return "ETF"
        
        if code.startswith('16'):
            return "LOF"
        
        if code.startswith('50') or code.startswith('18') or code.startswith('150'):
            return "MUTUAL_FUND"
        
        if code.startswith('0'):
            return "MUTUAL_FUND"
        
        return "STOCK"
        
    except Exception as e:
        return f"UNKNOWN (error: {str(e)})"


def get_akshare_fund_holdings(
    ticker: Annotated[str, "ticker symbol of the fund"],
    top_n: Annotated[int, "number of top holdings to return"] = 10,
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share fund holdings data from akshare.
    
    Args:
        ticker: 6-digit fund code (e.g., '110022' for E Fund Consumption)
        top_n: Number of top holdings to return
        curr_date: Current date
    
    Returns:
        Formatted string with fund holdings information
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Fund Holdings for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: Akshare (东方财富)\n\n"
        lines.append(header)
        
        holdings_found = False
        
        try:
            latest_date = datetime.now().strftime("%Y%m%d")
            df = ak.fund_portfolio_hold_em(date=latest_date)
            
            if df is not None and not df.empty:
                fund_holdings = df[df.iloc[:, 0].astype(str).str.contains(ticker, na=False)]
                
                if not fund_holdings.empty:
                    lines.append("## Fund Holdings:\n")
                    lines.append(_df_to_string(fund_holdings.head(top_n)))
                    lines.append("\n")
                    holdings_found = True
        except Exception:
            pass
        
        try:
            df = ak.fund_hold_structure_em(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("## Holding Structure:\n")
                lines.append(_df_to_string(df.head(top_n)))
                lines.append("\n")
                holdings_found = True
        except Exception:
            pass
        
        try:
            df = ak.fund_portfolio_industry_allocation_em(date=datetime.now().strftime("%Y%m%d"))
            if df is not None and not df.empty:
                lines.append("## Industry Allocation (Market Overview):\n")
                lines.append(_df_to_string(df.head(top_n)))
                lines.append("\n")
        except Exception:
            pass
        
        if not holdings_found:
            lines.append("Note: Detailed holdings data may not be available for this fund.\n")
            lines.append("Fund holdings are typically disclosed quarterly in China.\n")
            lines.append("Please refer to the fund's quarterly report for detailed holdings.\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fund holdings for {ticker}: {str(e)}"


def get_akshare_fund_nav(
    ticker: Annotated[str, "ticker symbol of the fund"],
    period: Annotated[str, "time period"] = "1y",
    calculate_drawdown: Annotated[bool, "whether to calculate drawdown"] = True,
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share fund Net Asset Value (NAV) history from akshare.
    
    Args:
        ticker: 6-digit fund code
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        calculate_drawdown: Whether to calculate drawdown metrics
        curr_date: Current date
    
    Returns:
        Formatted string with NAV history
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Fund NAV History for {ticker}\n"
        header += f"# Period: {period}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: Akshare (东方财富)\n\n"
        lines.append(header)
        
        try:
            df = ak.fund_open_fund_info_em(symbol=ticker, indicator="单位净值走势")
            
            if df is not None and not df.empty:
                period_days = {
                    "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
                    "6mo": 180, "1y": 365, "2y": 730, "5y": 1825,
                    "10y": 3650, "ytd": 365, "max": 36500
                }
                days = period_days.get(period, 365)
                
                if len(df) > days:
                    df = df.tail(days)
                
                if '净值日期' in df.columns:
                    df = df.sort_values('净值日期', ascending=False)
                
                lines.append("## NAV Summary:\n")
                lines.append(f"Total data points: {len(df)}\n")
                
                if '单位净值' in df.columns:
                    df['单位净值'] = pd.to_numeric(df['单位净值'], errors='coerce')
                    
                    latest_nav = df['单位净值'].iloc[0] if len(df) > 0 else None
                    highest_nav = df['单位净值'].max()
                    lowest_nav = df['单位净值'].min()
                    
                    if latest_nav is not None:
                        lines.append(f"Latest NAV: {latest_nav:.4f}\n")
                    if highest_nav is not None:
                        lines.append(f"Highest NAV in period: {highest_nav:.4f}\n")
                    if lowest_nav is not None:
                        lines.append(f"Lowest NAV in period: {lowest_nav:.4f}\n")
                    
                    if calculate_drawdown and len(df) > 1:
                        nav_series = df['单位净值'].dropna()
                        if len(nav_series) > 0:
                            rolling_max = nav_series.cummax()
                            drawdown = (nav_series - rolling_max) / rolling_max
                            max_drawdown = drawdown.min()
                            lines.append(f"Maximum Drawdown: {max_drawdown:.2%}\n")
                
                lines.append("\n## Recent NAV Data (Last 10 entries):\n")
                
                column_mapping = {
                    '净值日期': 'Date',
                    '单位净值': 'NAV',
                    '累计净值': 'Accumulated NAV',
                    '日增长率': 'Daily Change (%)',
                }
                df_display = df.rename(columns=column_mapping)
                lines.append(_df_to_string(df_display.head(10)))
                
            else:
                lines.append("No NAV data available for this fund.\n")
        except Exception as e:
            lines.append(f"Note: NAV data not available. Error: {e}\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fund NAV for {ticker}: {str(e)}"


def get_akshare_fund_manager_info(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share fund manager information from akshare.
    
    Args:
        ticker: 6-digit fund code
        curr_date: Current date
    
    Returns:
        Formatted string with fund manager information
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Fund Manager Information for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Data source: Akshare (东方财富)\n\n"
        lines.append(header)
        
        info_found = False
        
        try:
            df = ak.fund_overview_em(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("## Fund Overview:\n")
                
                for _, row in df.iterrows():
                    for col in df.columns:
                        value = row.get(col)
                        if value is not None and str(value).strip():
                            lines.append(f"{col}: {value}")
                
                lines.append("\n")
                info_found = True
        except Exception:
            pass
        
        try:
            df = ak.fund_manager_em()
            if df is not None and not df.empty:
                manager_cols = df.columns if len(df.columns) > 0 else []
                if '现任基金代码' in manager_cols:
                    fund_managers = df[df['现任基金代码'].astype(str).str.contains(ticker, na=False)]
                    
                    if not fund_managers.empty:
                        lines.append("## Fund Manager Information:\n")
                        
                        column_mapping = {
                            '序号': 'No.',
                            '姓名': 'Name',
                            '所属公司': 'Company',
                            '现任基金代码': 'Fund Code',
                            '现任基金': 'Fund Name',
                            '累计从业时间': 'Experience (Days)',
                            '现任基金资产总规模': 'AUM (Billion)',
                            '现任基金最佳回报': 'Best Return (%)',
                        }
                        
                        fund_managers_display = fund_managers.rename(columns=column_mapping)
                        lines.append(_df_to_string(fund_managers_display))
                        lines.append("\n")
                        info_found = True
        except Exception:
            pass
        
        if not info_found:
            lines.append("Note: Detailed fund manager information not available.\n")
            lines.append("Please refer to the fund's official website or prospectus.\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fund manager info for {ticker}: {str(e)}"


def get_akshare_fund_expense_ratio(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share fund expense ratio information from akshare.
    
    Args:
        ticker: 6-digit fund code
        curr_date: Current date
    
    Returns:
        Formatted string with expense ratio information
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Fund Expense Information for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        try:
            df = ak.fund_overview_em(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("## Fund Expense Information:\n")
                
                for _, row in df.iterrows():
                    for col in df.columns:
                        col_str = str(col).lower()
                        if '费率' in col_str or 'rate' in col_str or 'fee' in col_str or '管理费' in col_str or '托管费' in col_str:
                            value = row.get(col)
                            if value is not None and str(value).strip():
                                lines.append(f"{col}: {value}")
                
                lines.append("\n")
            else:
                lines.append("No expense data available for this fund.\n")
        except Exception as e:
            lines.append(f"Note: Expense data not available. Error: {e}\n")
        
        lines.append("## Typical A-Share Fund Expenses:\n")
        lines.append("- Management Fee (管理费): Typically 1.5% for equity funds, 0.5-1.0% for bond funds\n")
        lines.append("- Custodian Fee (托管费): Typically 0.25%\n")
        lines.append("- Sales Service Fee (销售服务费): Typically 0.25-0.4%\n")
        lines.append("- Redemption Fee (赎回费): Typically 0.5% if held less than 1 year\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fund expense info for {ticker}: {str(e)}"


def get_akshare_fund_risk_metrics(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get A-share fund risk metrics from akshare.
    
    Args:
        ticker: 6-digit fund code
        curr_date: Current date
    
    Returns:
        Formatted string with risk metrics
    """
    try:
        ak = _get_akshare()
        
        lines = []
        header = f"# A-Share Fund Risk Metrics for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        try:
            df = ak.fund_individual_analysis_xq(symbol=ticker)
            if df is not None and not df.empty:
                lines.append("## Risk Analysis (Xueqiu):\n")
                lines.append(_df_to_string(df))
                lines.append("\n")
            else:
                lines.append("Calculating risk metrics from NAV data...\n\n")
        except Exception:
            pass
        
        try:
            df = ak.fund_open_fund_info_em(symbol=ticker, indicator="单位净值走势")
            if df is not None and not df.empty and '单位净值' in df.columns:
                df['单位净值'] = pd.to_numeric(df['单位净值'], errors='coerce')
                nav_series = df['单位净值'].dropna()
                
                if len(nav_series) > 1:
                    daily_returns = nav_series.pct_change().dropna()
                    
                    lines.append("## Calculated Risk Metrics from NAV Data:\n")
                    lines.append(f"Data points used: {len(daily_returns)}\n")
                    
                    if len(daily_returns) > 0:
                        annualized_return = ((1 + daily_returns.mean()) ** 252 - 1) * 100
                        annualized_vol = daily_returns.std() * (252 ** 0.5) * 100
                        
                        lines.append(f"Annualized Return (approx): {annualized_return:.2f}%\n")
                        lines.append(f"Annualized Volatility (approx): {annualized_vol:.2f}%\n")
                        
                        rolling_max = nav_series.cummax()
                        drawdown = (nav_series - rolling_max) / rolling_max
                        max_drawdown = drawdown.min() * 100
                        lines.append(f"Maximum Drawdown: {max_drawdown:.2f}%\n")
                    
                    lines.append("\n")
        except Exception as e:
            lines.append(f"Note: Risk calculation from NAV failed. Error: {e}\n")
        
        lines.append("## Important Notes for A-Share Fund Risk Analysis:\n")
        lines.append("1. Beta, Alpha, and Sharpe Ratio require benchmark comparison\n")
        lines.append("2. For comprehensive risk analysis, compare against relevant indices:\n")
        lines.append("   - Equity funds: Compare against CSI 300 or CSI 500\n")
        lines.append("   - Bond funds: Compare against China Bond Aggregate Index\n")
        lines.append("3. Maximum Drawdown is a key risk metric for Chinese investors\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fund risk metrics for {ticker}: {str(e)}"


def get_akshare_fund_overview(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date"] = None
) -> str:
    """
    Get a comprehensive overview of an A-share fund.
    
    Args:
        ticker: 6-digit fund code
        curr_date: Current date
    
    Returns:
        Formatted string with comprehensive fund overview
    """
    try:
        lines = []
        header = f"# A-Share Fund Overview for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        asset_type = detect_akshare_asset_type(ticker)
        lines.append(f"## Asset Type: {asset_type}\n\n")
        
        manager_info = get_akshare_fund_manager_info(ticker, curr_date)
        if "Error" not in manager_info:
            lines.append("## Basic Information:\n")
            lines.append(manager_info.replace(f"# A-Share Fund Manager Information for {ticker}\n", ""))
            lines.append("\n")
        
        nav_info = get_akshare_fund_nav(ticker, "1y", True, curr_date)
        if "Error" not in nav_info:
            lines.append("## NAV Information:\n")
            lines.append(nav_info.split("## Recent NAV Data")[0].replace(f"# A-Share Fund NAV History for {ticker}\n", ""))
            lines.append("\n")
        
        expense_info = get_akshare_fund_expense_ratio(ticker, curr_date)
        if "Error" not in expense_info:
            lines.append("## Expense Information:\n")
            lines.append(expense_info.split("## Typical A-Share Fund Expenses")[0].replace(f"# A-Share Fund Expense Information for {ticker}\n", ""))
            lines.append("\n")
        
        lines.append("## Important Considerations for A-Share Funds:\n")
        lines.append("- This data is sourced from Akshare (东方财富) and may be incomplete\n")
        lines.append("- Always verify critical information with the fund's official documentation\n")
        lines.append("- Past performance does not guarantee future results\n")
        lines.append("- Chinese mutual funds are regulated by CSRC (中国证监会)\n")
        lines.append("- Consider consulting a licensed financial advisor before investing\n")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error retrieving A-share fund overview for {ticker}: {str(e)}"
