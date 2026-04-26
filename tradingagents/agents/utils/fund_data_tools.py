from langchain_core.tools import tool
from typing import Annotated, Optional
from tradingagents.dataflows.interface import route_to_vendor


@tool
def detect_asset_type(
    ticker: Annotated[str, "ticker symbol to detect asset type"]
) -> str:
    """
    Detect if a ticker represents a Stock, ETF, or Mutual Fund.
    
    This tool helps the system determine whether to use stock-specific analysis
    or fund-specific analysis.
    
    Args:
        ticker (str): Ticker symbol to check (e.g., AAPL, SPY, QQQ)
    
    Returns:
        str: One of 'STOCK', 'ETF', 'MUTUAL_FUND', 'FUND', 'POSSIBLE_FUND', or 'UNKNOWN'
        
    Note:
        - 'STOCK': Regular company stock
        - 'ETF': Exchange Traded Fund
        - 'MUTUAL_FUND': Mutual Fund
        - 'FUND': Detected as fund but specific type unclear
        - 'POSSIBLE_FUND': Has fund characteristics but not confirmed
        - 'UNKNOWN': Could not determine asset type
    """
    return route_to_vendor("detect_asset_type", ticker)


@tool
def get_fund_holdings(
    ticker: Annotated[str, "ticker symbol of the fund"],
    top_n: Annotated[int, "number of top holdings to return"] = 10,
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Get fund holdings information for ETFs and Mutual Funds.
    
    Retrieves information about the top stocks or assets held by the fund.
    This includes institutional holders, major holders, and sector exposures.
    
    Args:
        ticker (str): Ticker symbol of the fund (e.g., SPY, QQQ, VOO)
        top_n (int): Number of top holdings to return (default: 10)
        curr_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A formatted report containing fund holdings information
        
    Note:
        - Some funds may not disclose detailed holdings
        - If data is unavailable, the report will indicate this
        - Holdings data is typically updated quarterly for most funds
    """
    return route_to_vendor("get_fund_holdings", ticker, top_n, curr_date)


@tool
def get_fund_nav(
    ticker: Annotated[str, "ticker symbol of the fund"],
    period: Annotated[str, "time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"] = "1y",
    calculate_drawdown: Annotated[bool, "whether to calculate max drawdown"] = True,
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Get Net Asset Value (NAV) history and drawdown data for a fund.
    
    For ETFs, this uses historical price data as a proxy for NAV.
    Includes drawdown analysis shows the maximum loss from peak to trough.
    
    Args:
        ticker (str): Ticker symbol of the fund
        period (str): Time period for historical data
            Options: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
        calculate_drawdown (bool): Whether to calculate drawdown metrics
        curr_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A formatted report containing NAV history and drawdown analysis
        
    Important:
        - Drawdown is a key risk metric for fund evaluation
        - Maximum drawdown shows the worst historical loss
        - 30-day drawdown shows recent risk exposure
    """
    return route_to_vendor("get_fund_nav", ticker, period, calculate_drawdown, curr_date)


@tool
def get_fund_manager_info(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Get fund manager information and basic fund details.
    
    Retrieves information about the fund manager, fund family,
    inception date, and other management-related information.
    
    Args:
        ticker (str): Ticker symbol of the fund
        curr_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A formatted report containing fund manager information
        
    Note:
        - Fund tenure is an important factor in fund evaluation
        - Longer manager tenure may indicate more stable management
        - Fund family can indicate the overall investment style
    """
    return route_to_vendor("get_fund_manager_info", ticker, curr_date)


@tool
def get_fund_expense_ratio(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Get fund expense ratio, total assets, and other cost information.
    
    Expense ratio is a critical factor in long-term fund performance.
    Lower expense ratios generally lead to better net returns over time.
    
    Args:
        ticker (str): Ticker symbol of the fund
        curr_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A formatted report containing expense ratio and cost information
        
    Key Information:
        - Expense Ratio: Annual fee as percentage of assets
        - Total Assets: Fund size (AUM)
        - Net Assets: Net asset value
        - Category: Fund category (e.g., Large Growth, etc.)
        
    Note:
        - ETFs typically have lower expense ratios than mutual funds
        - Index funds generally have lower expenses than actively managed funds
        - Consider expense ratio relative to fund category averages
    """
    return route_to_vendor("get_fund_expense_ratio", ticker, curr_date)


@tool
def get_fund_risk_metrics(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Get fund risk metrics including beta, sharpe ratio, alpha, max drawdown, etc.
    
    These metrics help evaluate the risk-adjusted performance of a fund.
    
    Args:
        ticker (str): Ticker symbol of the fund
        curr_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A formatted report containing risk and performance metrics
        
    Key Metrics Explained:
        - Beta: Volatility relative to market (1.0 = market-like)
        - Alpha: Excess return vs benchmark (positive = outperformance)
        - Sharpe Ratio: Risk-adjusted return (higher = better)
        - Standard Deviation: Volatility measure (higher = riskier)
        - Max Drawdown: Worst peak-to-trough loss
        - Treynor Ratio: Return per unit of systematic risk
        
    Note:
        - Some metrics require benchmark comparison and may not be available
        - Always consider multiple metrics together for comprehensive evaluation
        - Past performance does not guarantee future results
    """
    return route_to_vendor("get_fund_risk_metrics", ticker, curr_date)


@tool
def get_fund_overview(
    ticker: Annotated[str, "ticker symbol of the fund"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """
    Get a comprehensive overview of a fund, combining all relevant information.
    
    This is a convenience tool that aggregates data from multiple sources
    including asset type, manager info, expense ratio, and risk metrics.
    
    Args:
        ticker (str): Ticker symbol of the fund
        curr_date (str): Current date in yyyy-mm-dd format
    
    Returns:
        str: A comprehensive formatted report with fund overview
        
    Note:
        - This tool combines information from multiple specific tools
        - Use for initial fund analysis for a complete picture
        - For detailed analysis, use the specific tools like get_fund_risk_metrics
    """
    return route_to_vendor("get_fund_overview", ticker, curr_date)
