from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
from .stockstats_utils import StockstatsUtils
from .yfinance_utils import YFRateLimitError, yfinance_retry, yfinance_cached

@yfinance_retry()
def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string

def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    # Optimized: Get stock data once and calculate indicators for all dates
    try:
        indicator_data = _get_stock_stats_bulk(symbol, indicator, curr_date)
        
        # Generate the date range we need
        current_dt = curr_date_dt
        date_values = []
        
        while current_dt >= before:
            date_str = current_dt.strftime('%Y-%m-%d')
            
            # Look up the indicator value for this date
            if date_str in indicator_data:
                indicator_value = indicator_data[date_str]
            else:
                indicator_value = "N/A: Not a trading day (weekend or holiday)"
            
            date_values.append((date_str, indicator_value))
            current_dt = current_dt - relativedelta(days=1)
        
        # Build the result string
        ind_string = ""
        for date_str, value in date_values:
            ind_string += f"{date_str}: {value}\n"
        
    except Exception as e:
        print(f"Error getting bulk stockstats data: {e}")
        # Fallback to original implementation if bulk method fails
        ind_string = ""
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        while curr_date_dt >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date_dt.strftime("%Y-%m-%d")
            )
            ind_string += f"{curr_date_dt.strftime('%Y-%m-%d')}: {indicator_value}\n"
            curr_date_dt = curr_date_dt - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def _get_stock_stats_bulk(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to calculate"],
    curr_date: Annotated[str, "current date for reference"]
) -> dict:
    """
    Optimized bulk calculation of stock stats indicators.
    Fetches data once and calculates indicator for all available dates.
    Returns dict mapping date strings to indicator values.
    """
    from .config import get_config
    import pandas as pd
    from stockstats import wrap
    import os
    
    config = get_config()
    online = config["data_vendors"]["technical_indicators"] != "local"
    
    if not online:
        # Local data path
        try:
            data = pd.read_csv(
                os.path.join(
                    config.get("data_cache_dir", "data"),
                    f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                )
            )
            df = wrap(data)
        except FileNotFoundError:
            raise Exception("Stockstats fail: Yahoo Finance data not fetched yet!")
    else:
        # Online data fetching with caching
        today_date = pd.Timestamp.today()
        curr_date_dt = pd.to_datetime(curr_date)
        
        end_date = today_date
        start_date = today_date - pd.DateOffset(years=15)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        data_file = os.path.join(
            config["data_cache_dir"],
            f"{symbol}-YFin-data-{start_date_str}-{end_date_str}.csv",
        )
        
        if os.path.exists(data_file):
            data = pd.read_csv(data_file)
            data["Date"] = pd.to_datetime(data["Date"])
        else:
            data = yf.download(
                symbol,
                start=start_date_str,
                end=end_date_str,
                multi_level_index=False,
                progress=False,
                auto_adjust=True,
            )
            data = data.reset_index()
            data.to_csv(data_file, index=False)
        
        df = wrap(data)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    
    # Calculate the indicator for all rows at once
    df[indicator]  # This triggers stockstats to calculate the indicator
    
    # Create a dictionary mapping date strings to indicator values
    result_dict = {}
    for _, row in df.iterrows():
        date_str = row["Date"]
        indicator_value = row[indicator]
        
        # Handle NaN/None values
        if pd.isna(indicator_value):
            result_dict[date_str] = "N/A"
        else:
            result_dict[date_str] = str(indicator_value)
    
    return result_dict


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
) -> str:

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date_dt.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)


@yfinance_retry()
@yfinance_cached()
def get_fundamentals(
    ticker: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get company fundamentals overview from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        info = ticker_obj.info

        if not info:
            return f"No fundamentals data found for symbol '{ticker}'"

        fields = [
            ("Name", info.get("longName")),
            ("Sector", info.get("sector")),
            ("Industry", info.get("industry")),
            ("Market Cap", info.get("marketCap")),
            ("PE Ratio (TTM)", info.get("trailingPE")),
            ("Forward PE", info.get("forwardPE")),
            ("PEG Ratio", info.get("pegRatio")),
            ("Price to Book", info.get("priceToBook")),
            ("EPS (TTM)", info.get("trailingEps")),
            ("Forward EPS", info.get("forwardEps")),
            ("Dividend Yield", info.get("dividendYield")),
            ("Beta", info.get("beta")),
            ("52 Week High", info.get("fiftyTwoWeekHigh")),
            ("52 Week Low", info.get("fiftyTwoWeekLow")),
            ("50 Day Average", info.get("fiftyDayAverage")),
            ("200 Day Average", info.get("twoHundredDayAverage")),
            ("Revenue (TTM)", info.get("totalRevenue")),
            ("Gross Profit", info.get("grossProfits")),
            ("EBITDA", info.get("ebitda")),
            ("Net Income", info.get("netIncomeToCommon")),
            ("Profit Margin", info.get("profitMargins")),
            ("Operating Margin", info.get("operatingMargins")),
            ("Return on Equity", info.get("returnOnEquity")),
            ("Return on Assets", info.get("returnOnAssets")),
            ("Debt to Equity", info.get("debtToEquity")),
            ("Current Ratio", info.get("currentRatio")),
            ("Book Value", info.get("bookValue")),
            ("Free Cash Flow", info.get("freeCashflow")),
        ]

        lines = []
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        header = f"# Company Fundamentals for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + "\n".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving fundamentals for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_balance_sheet(
    ticker: Annotated[str, "ticker symbol of the company"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get balance sheet data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        if freq.lower() == "quarterly":
            data = ticker_obj.quarterly_balance_sheet
        else:
            data = ticker_obj.balance_sheet
            
        if data.empty:
            return f"No balance sheet data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Balance Sheet data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving balance sheet for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_cashflow(
    ticker: Annotated[str, "ticker symbol of the company"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get cash flow data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        if freq.lower() == "quarterly":
            data = ticker_obj.quarterly_cashflow
        else:
            data = ticker_obj.cashflow
            
        if data.empty:
            return f"No cash flow data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Cash Flow data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving cash flow for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_income_statement(
    ticker: Annotated[str, "ticker symbol of the company"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
):
    """Get income statement data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        if freq.lower() == "quarterly":
            data = ticker_obj.quarterly_income_stmt
        else:
            data = ticker_obj.income_stmt
            
        if data.empty:
            return f"No income statement data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Income Statement data for {ticker.upper()} ({freq})\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving income statement for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_insider_transactions(
    ticker: Annotated[str, "ticker symbol of the company"]
):
    """Get insider transactions data from yfinance."""
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        data = ticker_obj.insider_transactions
        
        if data is None or data.empty:
            return f"No insider transactions data found for symbol '{ticker}'"
            
        # Convert to CSV string for consistency with other functions
        csv_string = data.to_csv()
        
        # Add header information
        header = f"# Insider Transactions data for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return header + csv_string

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving insider transactions for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def detect_asset_type(
    ticker: Annotated[str, "ticker symbol to detect asset type"]
) -> str:
    """
    Detect if a ticker represents a Stock, ETF, or Mutual Fund.
    
    Returns:
        str: One of 'STOCK', 'ETF', 'MUTUAL_FUND', 'UNKNOWN'
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        try:
            fast_info = ticker_obj.fast_info
            quote_type = fast_info.quote_type
        except Exception:
            quote_type = None
        
        if not quote_type:
            try:
                info = ticker_obj.info
                if info:
                    quote_type = info.get('quoteType', '').upper()
            except Exception:
                pass
        
        if not quote_type:
            return "UNKNOWN"
        
        quote_type = quote_type.upper()
        
        if quote_type == 'ETF':
            return 'ETF'
        elif quote_type == 'MUTUALFUND':
            return 'MUTUAL_FUND'
        elif quote_type in ['EQUITY', 'STOCK']:
            return 'STOCK'
        else:
            try:
                info = ticker_obj.info
                if info and info.get('fundFamily'):
                    return 'FUND'
                if info and info.get('expenseRatio') is not None:
                    return 'POSSIBLE_FUND'
            except Exception:
                pass
            return quote_type

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"UNKNOWN (error: {str(e)})"


@yfinance_retry()
@yfinance_cached()
def get_fund_holdings(
    ticker: Annotated[str, "ticker symbol of the fund"],
    top_n: Annotated[int, "number of top holdings to return"] = 10,
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
) -> str:
    """
    Get fund holdings (top stocks held by ETF/Mutual Fund).
    
    Args:
        ticker: Ticker symbol of the fund (e.g., SPY, QQQ)
        top_n: Number of top holdings to return
        curr_date: Current date (for compatibility with caching)
    
    Returns:
        Formatted string with fund holdings information
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        lines = []
        header = f"# Fund Holdings for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        holdings_found = False
        
        try:
            funds_data = ticker_obj.funds_data
            if funds_data is not None and hasattr(funds_data, 'top_holdings'):
                top_holdings = funds_data.top_holdings
                if top_holdings is not None and not top_holdings.empty:
                    lines.append("## Top Holdings (from funds_data):\n")
                    lines.append(top_holdings.head(top_n).to_string())
                    lines.append("\n")
                    holdings_found = True
        except Exception:
            pass
        
        try:
            info = ticker_obj.info
            if info:
                for key in info.keys():
                    if 'holding' in key.lower() or 'sector' in key.lower() or 'weight' in key.lower():
                        value = info.get(key)
                        if value is not None:
                            lines.append(f"## {key}:\n")
                            lines.append(str(value))
                            lines.append("\n")
                            holdings_found = True
        except Exception:
            pass
        
        try:
            inst_holders = ticker_obj.institutional_holders
            if inst_holders is not None and not inst_holders.empty:
                lines.append("## Institutional Holders:\n")
                lines.append(inst_holders.head(top_n).to_string())
                lines.append("\n")
        except Exception:
            pass
        
        try:
            major_holders = ticker_obj.major_holders
            if major_holders is not None:
                lines.append("## Major Holders:\n")
                lines.append(str(major_holders))
                lines.append("\n")
        except Exception:
            pass
        
        if not holdings_found:
            lines.append("Note: Detailed holdings data not available for this fund.\n")
            lines.append("This is common for certain ETFs and mutual funds.\n")
            lines.append("Please refer to the fund's official website for holdings information.\n")
        
        return "".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving fund holdings for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_fund_nav(
    ticker: Annotated[str, "ticker symbol of the fund"],
    period: Annotated[str, "time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"] = "1y",
    calculate_drawdown: Annotated[bool, "whether to calculate max drawdown"] = True,
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
) -> str:
    """
    Get Net Asset Value (NAV) history and drawdown data for a fund.
    
    For ETFs, this uses historical price data as a proxy for NAV.
    
    Args:
        ticker: Ticker symbol of the fund
        period: Time period for historical data
        calculate_drawdown: Whether to calculate drawdown metrics
        curr_date: Current date (for compatibility)
    
    Returns:
        Formatted string with NAV history and drawdown information
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        hist = ticker_obj.history(period=period)
        
        if hist.empty:
            return f"No NAV/price data found for symbol '{ticker}' for period '{period}'"
        
        lines = []
        header = f"# Fund NAV/Price History for {ticker.upper()}\n"
        header += f"# Period: {period}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        if hist.index.tz is not None:
            hist.index = hist.index.tz_localize(None)
        
        if 'Close' in hist.columns:
            latest_close = hist['Close'].iloc[-1]
            highest_close = hist['Close'].max()
            lowest_close = hist['Close'].min()
            
            lines.append(f"## Summary Statistics ({period}):\n")
            lines.append(f"Latest Price/NAV: {latest_close:.4f}\n")
            lines.append(f"Highest Price/NAV: {highest_close:.4f}\n")
            lines.append(f"Lowest Price/NAV: {lowest_close:.4f}\n")
            lines.append(f"Total data points: {len(hist)}\n\n")
        
        if calculate_drawdown and 'Close' in hist.columns:
            rolling_max = hist['Close'].cummax()
            drawdown = (hist['Close'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            max_drawdown_date = drawdown.idxmin()
            
            lines.append(f"## Drawdown Analysis:\n")
            lines.append(f"Maximum Drawdown: {max_drawdown:.2%}\n")
            lines.append(f"Date of Max Drawdown: {max_drawdown_date}\n\n")
            
            if len(hist) >= 30:
                recent_30d = hist.tail(30)
                rolling_max_30 = recent_30d['Close'].cummax()
                drawdown_30 = (recent_30d['Close'] - rolling_max_30) / rolling_max_30
                max_dd_30 = drawdown_30.min()
                lines.append(f"30-Day Max Drawdown: {max_dd_30:.2%}\n\n")
        
        lines.append(f"## Recent Price/NAV Data (Last 10 entries):\n")
        numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
        for col in numeric_columns:
            if col in hist.columns:
                hist[col] = hist[col].round(4)
        
        lines.append(hist.tail(10).to_string())
        lines.append("\n")
        
        return "".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving NAV data for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_fund_manager_info(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
) -> str:
    """
    Get fund manager information and past performance.
    
    Args:
        ticker: Ticker symbol of the fund
        curr_date: Current date (for compatibility)
    
    Returns:
        Formatted string with fund manager information
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        lines = []
        header = f"# Fund Manager Information for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        info_found = False
        
        try:
            info = ticker_obj.info
            if info:
                manager_fields = [
                    ('fundFamily', 'Fund Family'),
                    ('fundInceptionDate', 'Fund Inception Date'),
                    ('legalType', 'Legal Type'),
                    ('managementInfo', 'Management Info'),
                    ('managerName', 'Manager Name'),
                    ('portfolioName', 'Portfolio Name'),
                    ('longName', 'Fund Full Name'),
                    ('shortName', 'Fund Short Name'),
                ]
                
                for info_key, display_name in manager_fields:
                    value = info.get(info_key)
                    if value is not None:
                        if info_key == 'fundInceptionDate':
                            try:
                                if isinstance(value, (int, float)):
                                    from datetime import datetime as dt
                                    value = dt.fromtimestamp(value).strftime('%Y-%m-%d')
                            except Exception:
                                pass
                        lines.append(f"{display_name}: {value}\n")
                        info_found = True
        except Exception:
            pass
        
        if not info_found:
            lines.append("Note: Detailed fund manager information not available.\n")
            lines.append("This data may not be accessible for certain funds.\n")
        
        try:
            fast_info = ticker_obj.fast_info
            lines.append(f"\n## Quick Info:\n")
            lines.append(f"Quote Type: {fast_info.quote_type}\n")
            lines.append(f"Currency: {fast_info.currency}\n")
            lines.append(f"Exchange: {fast_info.exchange}\n")
        except Exception:
            pass
        
        return "".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving fund manager info for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_fund_expense_ratio(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
) -> str:
    """
    Get fund expense ratio, total assets, and other basic information.
    
    Args:
        ticker: Ticker symbol of the fund
        curr_date: Current date (for compatibility)
    
    Returns:
        Formatted string with expense ratio and fund information
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        lines = []
        header = f"# Fund Expense & Basic Information for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        info_found = False
        
        try:
            info = ticker_obj.info
            if info:
                expense_fields = [
                    ('expenseRatio', 'Expense Ratio'),
                    ('annualReportExpenseRatio', 'Annual Report Expense Ratio'),
                    ('grossExpenseRatio', 'Gross Expense Ratio'),
                    ('netExpenseRatio', 'Net Expense Ratio'),
                    ('totalAssets', 'Total Assets'),
                    ('netAssets', 'Net Assets'),
                    ('category', 'Category'),
                    ('investmentStrategy', 'Investment Strategy'),
                    ('fundObjective', 'Fund Objective'),
                ]
                
                for info_key, display_name in expense_fields:
                    value = info.get(info_key)
                    if value is not None:
                        if 'Ratio' in display_name and isinstance(value, (int, float)):
                            lines.append(f"{display_name}: {value:.4%}\n")
                        elif 'Assets' in display_name and isinstance(value, (int, float)):
                            lines.append(f"{display_name}: ${value:,.0f}\n")
                        else:
                            lines.append(f"{display_name}: {value}\n")
                        info_found = True
        except Exception:
            pass
        
        try:
            fast_info = ticker_obj.fast_info
            lines.append(f"\n## Market Data:\n")
            lines.append(f"Last Price: {fast_info.last_price:.4f}\n")
            lines.append(f"50-Day Average: {fast_info.fifty_day_average:.4f}\n")
            lines.append(f"200-Day Average: {fast_info.two_hundred_day_average:.4f}\n")
            lines.append(f"52-Week High: {fast_info.year_high:.4f}\n")
            lines.append(f"52-Week Low: {fast_info.year_low:.4f}\n")
            lines.append(f"Year-to-Date Change: {fast_info.year_change:.2%}\n")
        except Exception:
            pass
        
        if not info_found:
            lines.append("Note: Detailed expense information not available.\n")
        
        return "".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving expense info for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_fund_risk_metrics(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
) -> str:
    """
    Get fund risk metrics including beta, sharpe ratio, alpha, max drawdown, etc.
    
    Args:
        ticker: Ticker symbol of the fund
        curr_date: Current date (for compatibility)
    
    Returns:
        Formatted string with risk metrics
    """
    try:
        ticker_obj = yf.Ticker(ticker.upper())
        
        lines = []
        header = f"# Fund Risk Metrics for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        info_found = False
        
        try:
            info = ticker_obj.info
            if info:
                risk_fields = [
                    ('beta', 'Beta'),
                    ('beta3Year', 'Beta (3-Year)'),
                    ('beta5Year', 'Beta (5-Year)'),
                    ('sharpeRatio', 'Sharpe Ratio'),
                    ('sharpeRatio3Year', 'Sharpe Ratio (3-Year)'),
                    ('sharpeRatio5Year', 'Sharpe Ratio (5-Year)'),
                    ('alpha', 'Alpha'),
                    ('alpha3Year', 'Alpha (3-Year)'),
                    ('standardDeviation', 'Standard Deviation'),
                    ('standardDeviation3Year', 'Standard Deviation (3-Year)'),
                    ('treynorRatio', 'Treynor Ratio'),
                    ('maxDrawdown', 'Maximum Drawdown'),
                    ('ytdReturn', 'Year-to-Date Return'),
                    ('threeYearAverageReturn', '3-Year Average Return'),
                    ('fiveYearAverageReturn', '5-Year Average Return'),
                ]
                
                lines.append("## Risk & Performance Metrics:\n")
                for info_key, display_name in risk_fields:
                    value = info.get(info_key)
                    if value is not None:
                        if 'Return' in display_name or 'Drawdown' in display_name:
                            if isinstance(value, (int, float)):
                                lines.append(f"{display_name}: {value:.2%}\n")
                            else:
                                lines.append(f"{display_name}: {value}\n")
                        else:
                            lines.append(f"{display_name}: {value}\n")
                        info_found = True
        except Exception:
            pass
        
        try:
            hist = ticker_obj.history(period="1y")
            if not hist.empty and 'Close' in hist.columns:
                rolling_max = hist['Close'].cummax()
                drawdown = (hist['Close'] - rolling_max) / rolling_max
                max_dd = drawdown.min()
                
                lines.append(f"\n## Calculated Metrics (1-Year):\n")
                lines.append(f"Calculated Max Drawdown: {max_dd:.2%}\n")
                lines.append(f"Data points used: {len(hist)}\n")
        except Exception:
            pass
        
        if not info_found:
            lines.append("Note: Detailed risk metrics not available from yfinance.\n")
            lines.append("\n## Important Note for Fund Analysis:\n")
            lines.append("For comprehensive fund analysis, you should also consider:\n")
            lines.append("1. Using historical price data to calculate volatility and drawdown\n")
            lines.append("2. Comparing against relevant benchmarks (e.g., S&P 500 for equity funds)\n")
            lines.append("3. Reviewing the fund's prospectus and annual reports\n")
            lines.append("4. Checking the fund's official website for updated information\n")
        
        lines.append("\n## Data Availability Notes:\n")
        lines.append("- Some funds may not have all metrics available\n")
        lines.append("- Metrics like Sharpe Ratio and Alpha may require benchmark comparison\n")
        lines.append("- Always verify important data with official sources\n")
        
        return "".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving risk metrics for {ticker}: {str(e)}"


@yfinance_retry()
@yfinance_cached()
def get_fund_overview(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date (not used for yfinance)"] = None
) -> str:
    """
    Get a comprehensive overview of a fund, combining all relevant information.
    
    This is a convenience function that aggregates data from multiple sources.
    
    Args:
        ticker: Ticker symbol of the fund
        curr_date: Current date (for compatibility)
    
    Returns:
        Formatted string with comprehensive fund overview
    """
    try:
        lines = []
        header = f"# Fund Overview for {ticker.upper()}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        lines.append(header)
        
        asset_type = detect_asset_type(ticker)
        lines.append(f"## Asset Type: {asset_type}\n\n")
        
        manager_info = get_fund_manager_info(ticker, curr_date)
        if "Error" not in manager_info and "Note: Detailed" not in manager_info:
            lines.append("## Basic Information:\n")
            info_section = manager_info.split("## Quick Info:")[0] if "## Quick Info:" in manager_info else manager_info
            lines.append(info_section.replace(f"# Fund Manager Information for {ticker.upper()}\n", ""))
            lines.append("\n")
        
        expense_info = get_fund_expense_ratio(ticker, curr_date)
        if "Error" not in expense_info:
            lines.append("## Expense Information:\n")
            lines.append(expense_info.split("## Market Data:")[0].replace(f"# Fund Expense & Basic Information for {ticker.upper()}\n", ""))
            lines.append("\n")
        
        risk_metrics = get_fund_risk_metrics(ticker, curr_date)
        if "Error" not in risk_metrics and "Note: Detailed" not in risk_metrics:
            lines.append("## Risk Metrics:\n")
            lines.append(risk_metrics.split("## Data Availability Notes:")[0].replace(f"# Fund Risk Metrics for {ticker.upper()}\n", ""))
            lines.append("\n")
        
        lines.append("## Important Considerations:\n")
        lines.append("- This data is sourced from Yahoo Finance and may be incomplete\n")
        lines.append("- Always verify critical information with the fund's official documentation\n")
        lines.append("- Past performance does not guarantee future results\n")
        lines.append("- Consider consulting a financial advisor before making investment decisions\n")
        
        return "".join(lines)

    except YFRateLimitError:
        raise
    except Exception as e:
        return f"Error retrieving fund overview for {ticker}: {str(e)}"