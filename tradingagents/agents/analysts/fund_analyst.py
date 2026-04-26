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

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import (
    detect_asset_type,
    get_fund_holdings,
    get_fund_nav,
    get_fund_manager_info,
    get_fund_expense_ratio,
    get_fund_risk_metrics,
    get_fund_overview,
)
from tradingagents.dataflows.config import get_config


def create_fund_analyst(llm):
    def fund_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        asset_type = state.get("asset_type", "")

        tools = [
            detect_asset_type,
            get_fund_holdings,
            get_fund_nav,
            get_fund_manager_info,
            get_fund_expense_ratio,
            get_fund_risk_metrics,
            get_fund_overview,
        ]

        asset_type_note = ""
        if asset_type:
            asset_type_note = f"Detected asset type: {asset_type}. "

        system_message = (
            "You are a senior fund analyst tasked with analyzing Exchange Traded Funds (ETFs) and Mutual Funds. "
            "Please write a comprehensive report covering all critical aspects of the fund to inform trading decisions. "
            + asset_type_note
            + """

Key areas to analyze (use available tools to gather data):

1. FUND BASICS & MANAGEMENT (get_fund_manager_info, get_fund_expense_ratio):
   - Fund family and management team
   - Fund inception date and manager tenure
   - Expense ratio (compare to category averages)
   - Total assets under management (AUM)
   - Investment strategy and objective
   - Fund category and benchmark

2. HOLDINGS ANALYSIS (get_fund_holdings):
   - Top 10 holdings and their weights
   - Concentration risk (is the fund too concentrated in few stocks?)
   - Sector exposure and industry allocation
   - Turnover rate implications
   - Correlation among top holdings

3. PERFORMANCE & RISK METRICS (get_fund_nav, get_fund_risk_metrics):
   - Historical NAV performance trends
   - Maximum drawdown (peak-to-trough loss)
   - Beta (volatility vs benchmark)
   - Sharpe Ratio (risk-adjusted return)
   - Alpha (excess return vs benchmark)
   - Standard deviation (volatility)
   - Treynor Ratio (return per systematic risk unit)

4. COST ANALYSIS (get_fund_expense_ratio):
   - Gross vs net expense ratio
   - Expense ratio trend over time
   - Comparison to category average
   - Impact of expenses on long-term returns (1% cost difference over 10 years = significant impact)

5. COMPREHENSIVE OVERVIEW (get_fund_overview):
   - Use this tool for a quick summary of all available data
   - Fill in gaps with specific tools as needed

Important Considerations:
- Some funds may not have complete data available. If data is missing, state this clearly and analyze based on available information.
- For ETFs, consider tracking error vs the underlying index.
- For actively managed funds, focus on manager alpha and consistency.
- Consider tax efficiency for ETFs vs mutual funds.
- Liquidity: trading volume, bid-ask spread (for ETFs).
- Distribution policy: dividend yield, capital gains distribution history.

Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.

Use the available tools:
- `detect_asset_type`: Confirm if the ticker is ETF, Mutual Fund, or Stock
- `get_fund_holdings`: Get top holdings and sector exposure
- `get_fund_nav`: Get historical NAV/price data and drawdown analysis
- `get_fund_manager_info`: Get fund manager and basic fund info
- `get_fund_expense_ratio`: Get expense ratio and cost information
- `get_fund_risk_metrics`: Get risk metrics like Sharpe ratio, beta, alpha, max drawdown
- `get_fund_overview`: Get comprehensive overview combining all data

Note: If the asset type is detected as STOCK, this analyst is not the right choice. 
However, if you're already here, provide a brief note that this tool is designed for funds, not individual stocks.
"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The fund we want to analyze is {ticker}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fund_overview_report": report,
        }

    return fund_analyst_node


def create_dynamic_analyst_router():
    """
    Create a router node that routes to the appropriate analyst based on asset type.
    
    This router will:
    1. Detect asset type if not already known
    2. Route STOCK -> fundamentals_analyst path
    3. Route ETF/MUTUAL_FUND -> fund_analyst path
    """
    def router_node(state):
        from tradingagents.agents.utils.agent_utils import detect_asset_type as detect_tool
        
        ticker = state["company_of_interest"]
        current_asset_type = state.get("asset_type", "")
        
        if not current_asset_type or current_asset_type == "":
            try:
                result = detect_tool.invoke({"ticker": ticker})
                detected_type = result
                
                if isinstance(detected_type, str):
                    if "ETF" in detected_type:
                        current_asset_type = "ETF"
                    elif "MUTUAL_FUND" in detected_type or "MUTUALFUND" in detected_type:
                        current_asset_type = "MUTUAL_FUND"
                    elif "STOCK" in detected_type or "EQUITY" in detected_type:
                        current_asset_type = "STOCK"
                    else:
                        current_asset_type = detected_type
            except Exception as e:
                current_asset_type = "UNKNOWN"
        
        return {
            "asset_type": current_asset_type,
        }
    
    return router_node
