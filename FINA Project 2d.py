#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 18:11:16 2026

@author: Andrew
"""

# =============================================================================
# DCF Equity Valuation App
# FINA 4011/5011 - Project 2
# Team: Kristian Blagoev, Dom Dazzo, Andrew Kohlbrenner
#
# A polished, color-coded Streamlit app that pulls live financials from Yahoo
# Finance for any ticker, lets the user override every assumption, and walks
# through the full DCF in a tabbed layout.
# =============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# =============================================================================
# Page setup
# =============================================================================
st.set_page_config(
    page_title="DCF Valuation Studio",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# =============================================================================
# Custom CSS - locked light theme with explicit colors everywhere
# Belt-and-suspenders approach so the user's system dark mode cannot override.
# =============================================================================
st.markdown(
    """
    <style>
    /* ===== FORCE LIGHT THEME EVERYWHERE ===== */
    .stApp {
        background-color: #ffffff !important;
        color: #0a2540 !important;
    }
    .main .block-container {
        background-color: #ffffff !important;
        color: #0a2540 !important;
    }

    /* All text defaults to dark navy */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #0a2540 !important;
    }

    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #0a2540 !important;
    }

    /* Captions in muted grey */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #6b7280 !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #0a2540 !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #0a2540 !important;
        font-weight: 500 !important;
    }
    /* Sidebar input fields */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select {
        background-color: #ffffff !important;
        color: #0a2540 !important;
        border: 1px solid #cbd5e1 !important;
    }
    /* Sidebar number input +/- buttons */
    section[data-testid="stSidebar"] button {
        background-color: #ffffff !important;
        color: #0a2540 !important;
        border: 1px solid #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #e2e8f0 !important;
    }
    /* Sidebar slider track */
    section[data-testid="stSidebar"] [data-baseweb="slider"] {
        color: #0a2540 !important;
    }
    /* Sidebar header text */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #0a2540 !important;
        font-weight: 700 !important;
    }
    /* Sidebar tooltip "?" icon */
    section[data-testid="stSidebar"] [data-testid="stTooltipIcon"] {
        color: #2e7dd1 !important;
    }
    /* Sidebar help text on hover */
    [data-testid="stTooltipContent"] {
        background-color: #0a2540 !important;
        color: #ffffff !important;
    }

    /* ===== MAIN AREA INPUTS ===== */
    .stApp input, .stApp textarea, .stApp select {
        background-color: #ffffff !important;
        color: #0a2540 !important;
    }

    /* ===== HEADER BANNER ===== */
    .header-banner {
        background: linear-gradient(135deg, #0a2540 0%, #1e4d8b 50%, #2e7dd1 100%);
        padding: 28px 32px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .stApp .header-banner h1,
    .header-banner h1 {
        color: #ffffff !important;
        margin: 0 !important;
        font-size: 2.0rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    .stApp .header-banner p,
    .header-banner p {
        color: #cfe2ff !important;
        margin: 6px 0 0 0 !important;
        font-size: 0.95rem !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff !important;
        border-bottom: 2px solid #e5e7eb !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc !important;
        color: #475569 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e4d8b !important;
        color: #ffffff !important;
    }
    .stTabs [aria-selected="true"] * {
        color: #ffffff !important;
    }

    /* ===== SNAPSHOT CARDS ===== */
    .snap-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #2e7dd1;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 10px;
    }
    .snap-card .label {
        color: #6b7280 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .snap-card .value {
        color: #0a2540 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 4px;
    }

    /* ===== SECTION HEADINGS ===== */
    .section-head {
        color: #0a2540 !important;
        font-size: 1.20rem !important;
        font-weight: 700 !important;
        margin: 22px 0 10px 0 !important;
        padding-bottom: 8px;
        border-bottom: 3px solid #2e7dd1;
    }

    /* ===== COMPANY DESCRIPTION BOX ===== */
    .company-desc {
        background: #f8fafc;
        border-left: 4px solid #2e7dd1;
        padding: 16px 20px;
        border-radius: 6px;
        margin: 12px 0 18px 0;
        color: #334155 !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* ===== RESULT CARDS ===== */
    .result-card {
        padding: 20px 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .result-card.intrinsic {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px solid #2e7dd1;
    }
    .result-card.market {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 2px solid #64748b;
    }
    .result-card.under {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 2px solid #10b981;
    }
    .result-card.over {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #ef4444;
    }
    .result-card .rc-label {
        font-size: 0.85rem !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700 !important;
    }
    .result-card .rc-value {
        font-size: 2.0rem !important;
        font-weight: 700 !important;
        margin: 8px 0 !important;
        color: #0a2540 !important;
    }
    .result-card.under .rc-value { color: #047857 !important; }
    .result-card.over .rc-value { color: #b91c1c !important; }

    /* ===== DATAFRAMES ===== */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    /* Force dataframe text dark */
    [data-testid="stDataFrame"] * {
        color: #0a2540 !important;
    }

    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        color: #0a2540 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #0a2540 !important;
    }

    /* ===== EXPANDER ===== */
    [data-testid="stExpander"] {
        background-color: #f8fafc !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #0a2540 !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] * {
        color: #0a2540 !important;
    }

    /* ===== INFO/WARNING/ERROR BOXES ===== */
    [data-testid="stAlert"] {
        background-color: #eff6ff !important;
    }
    [data-testid="stAlert"] * {
        color: #0a2540 !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton button {
        background-color: #1e4d8b !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton button:hover {
        background-color: #2e7dd1 !important;
    }
    .stDownloadButton button * {
        color: #ffffff !important;
    }

    /* ===== FOOTER ===== */
    .app-footer {
        background: linear-gradient(135deg, #0a2540 0%, #1e4d8b 100%);
        color: #ffffff !important;
        padding: 24px 28px;
        border-radius: 12px;
        margin-top: 32px;
    }
    .stApp .app-footer,
    .stApp .app-footer * {
        color: #ffffff !important;
    }
    .stApp .app-footer .footer-title,
    .app-footer .footer-title {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    .stApp .app-footer .footer-desc,
    .app-footer .footer-desc {
        color: #cfe2ff !important;
        font-size: 0.92rem !important;
        line-height: 1.55;
        margin-bottom: 14px !important;
    }
    .app-footer .footer-team {
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 12px;
        font-size: 0.88rem !important;
    }
    .stApp .app-footer .footer-team .team-label,
    .app-footer .footer-team .team-label {
        color: #94c5ff !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
    }
    .stApp .app-footer .footer-team .team-names,
    .app-footer .footer-team .team-names {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-top: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Header banner
# =============================================================================
st.markdown(
    """
    <div class="header-banner">
        <h1>DCF Valuation Studio</h1>
        <p>FINA 4011/5011 - Project 2 &nbsp;|&nbsp; Live equity valuation using a Discounted Cash Flow model</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Sidebar: Ticker entry and assumption overrides
# =============================================================================
st.sidebar.markdown("### :mag: Company")
ticker_input = st.sidebar.text_input(
    "Ticker symbol",
    value="AAPL",
    help="Type any US-listed ticker (e.g., AAPL, MSFT, NVDA, KO, JPM, MEDP). Data is pulled from Yahoo Finance.",
).strip().upper()


@st.cache_data(ttl=3600, show_spinner="Fetching live data...")
def fetch_company_data(ticker: str):
    """Pull all needed financials in one place. Cached for one hour."""
    tk = yf.Ticker(ticker)
    info = tk.info
    if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
        raise ValueError(f"No data found for ticker '{ticker}'.")
    return info, tk.financials, tk.balance_sheet, tk.cashflow


try:
    info, financials, balance_sheet, cashflow = fetch_company_data(ticker_input)
    company_name = info.get("longName", ticker_input)
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares_out = info.get("sharesOutstanding") or 1
    market_cap = info.get("marketCap") or (current_price * shares_out)
    beta = info.get("beta") or 1.0
    total_debt = info.get("totalDebt") or 0
    total_cash = info.get("totalCash") or 0
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    business_summary = info.get("longBusinessSummary", "")
    fetch_ok = True
except Exception as e:
    st.sidebar.error(f"Could not load data for '{ticker_input}'. {e}")
    fetch_ok = False

if not fetch_ok:
    st.info("Enter a valid US ticker symbol in the sidebar to begin.")
    st.stop()

# =============================================================================
# Pull historical financials and compute defaults
# =============================================================================
hist_revenue, hist_ebit, hist_growth_default, avg_margin_default = (
    None, None, None, None,
)
try:
    rev_row = financials.loc["Total Revenue"].dropna().sort_index() / 1e6
    hist_revenue = rev_row

    if "EBIT" in financials.index:
        ebit_row = financials.loc["EBIT"].dropna().sort_index() / 1e6
    elif "Operating Income" in financials.index:
        ebit_row = financials.loc["Operating Income"].dropna().sort_index() / 1e6
    else:
        ebit_row = None
    hist_ebit = ebit_row

    if len(hist_revenue) >= 2:
        n = len(hist_revenue) - 1
        hist_growth_default = (hist_revenue.iloc[-1] / hist_revenue.iloc[0]) ** (1 / n) - 1
    if hist_ebit is not None and len(hist_ebit) > 0:
        avg_margin_default = (hist_ebit / hist_revenue.reindex(hist_ebit.index)).mean()
except Exception:
    pass

base_revenue_default = float(hist_revenue.iloc[-1]) if hist_revenue is not None and len(hist_revenue) > 0 else 1000.0
default_growth = float(hist_growth_default * 100) if hist_growth_default is not None else 5.0
default_growth = max(min(default_growth, 25.0), -10.0)
default_margin = float(avg_margin_default * 100) if avg_margin_default is not None else 15.0
default_margin = max(min(default_margin, 60.0), 1.0)

# =============================================================================
# Sidebar: Operating assumptions
# =============================================================================
st.sidebar.markdown("### :gear: Operating Assumptions")

base_revenue = st.sidebar.number_input(
    "Base year revenue ($M)",
    value=round(base_revenue_default, 1),
    help="Most recent annual revenue. Pulled live; override if you want.",
)
growth_rate = st.sidebar.number_input(
    "Revenue growth rate (%)",
    value=round(default_growth, 2),
    help="How fast you expect revenue to grow each year during the projection. Default = historical CAGR.",
) / 100
ebit_margin = st.sidebar.number_input(
    "EBIT margin (%)",
    value=round(default_margin, 2),
    help="Operating profit as a percent of revenue. Default = historical average.",
) / 100
tax_rate = st.sidebar.number_input(
    "Effective tax rate (%)", value=21.0,
    help="The US statutory rate is 21%. Most large companies pay 15-25%.",
) / 100
reinvest_rate = st.sidebar.number_input(
    "Reinvestment rate (% of NOPAT)", value=30.0,
    help="The portion of after-tax operating profit reinvested into capex and working capital. Higher growth usually means higher reinvestment.",
) / 100
projection_years = st.sidebar.slider(
    "Projection horizon (years)", 3, 10, 5,
    help="Number of years to forecast cash flows explicitly before applying terminal value.",
)

# =============================================================================
# Sidebar: Discount rate
# =============================================================================
st.sidebar.markdown("### :bank: Discount Rate (WACC)")

risk_free = st.sidebar.number_input(
    "Risk-free rate (%)", value=4.25,
    help="Typically the 10-year US Treasury yield. Around 4-5% recently.",
) / 100
erp = st.sidebar.number_input(
    "Equity risk premium (%)", value=5.5,
    help="Extra return investors demand for stocks vs. Treasuries. Damodaran's implied ERP is around 5-6%.",
) / 100
pretax_cost_debt = st.sidebar.number_input(
    "Pre-tax cost of debt (%)", value=5.5,
    help="The interest rate the company would pay if it borrowed today (risk-free rate + credit spread).",
) / 100

default_debt_weight = total_debt / (market_cap + total_debt) * 100 if market_cap and total_debt else 0.0
debt_weight = st.sidebar.slider(
    "Debt weight (%)",
    0.0, 100.0, float(round(default_debt_weight, 1)),
    help="Debt as a percent of total capital (D / (D + E)). Default uses live market cap and total debt.",
) / 100
equity_weight = 1 - debt_weight

cost_equity = risk_free + beta * erp
after_tax_cost_debt = pretax_cost_debt * (1 - tax_rate)
wacc = equity_weight * cost_equity + debt_weight * after_tax_cost_debt

# =============================================================================
# Sidebar: Terminal value and equity bridge
# =============================================================================
st.sidebar.markdown("### :infinity: Terminal Value")

terminal_growth = st.sidebar.number_input(
    "Terminal growth rate (%)", value=2.5,
    help="Long-run growth after the projection period. Should not exceed long-run GDP growth (~2-3%).",
) / 100

if terminal_growth >= wacc:
    st.sidebar.error("Terminal growth must be less than WACC.")
    st.stop()

st.sidebar.markdown("### :scales: Equity Bridge")
debt_input = st.sidebar.number_input(
    "Total debt ($M)", value=round(total_debt / 1e6, 1) if total_debt else 0.0,
    help="Subtracted from enterprise value to get equity value.",
)
cash_input = st.sidebar.number_input(
    "Cash & equivalents ($M)", value=round(total_cash / 1e6, 1) if total_cash else 0.0,
    help="Added to enterprise value (it belongs to shareholders).",
)
shares_input = st.sidebar.number_input(
    "Shares outstanding (M)", value=round(shares_out / 1e6, 1) if shares_out else 100.0,
    help="Equity value divided by shares = intrinsic value per share.",
)

# =============================================================================
# Run the DCF math
# =============================================================================
years = list(range(1, projection_years + 1))
revenues, ebits, nopats, reinvestments, fcfs, discount_factors, pv_fcfs = (
    [], [], [], [], [], [], [],
)
rev = base_revenue
for t in years:
    rev = rev * (1 + growth_rate)
    ebit = rev * ebit_margin
    nopat = ebit * (1 - tax_rate)
    reinvestment = nopat * reinvest_rate
    fcf = nopat - reinvestment
    df_factor = 1 / (1 + wacc) ** t
    pv = fcf * df_factor
    revenues.append(rev)
    ebits.append(ebit)
    nopats.append(nopat)
    reinvestments.append(reinvestment)
    fcfs.append(fcf)
    discount_factors.append(df_factor)
    pv_fcfs.append(pv)

terminal_fcf = fcfs[-1] * (1 + terminal_growth)
terminal_value = terminal_fcf / (wacc - terminal_growth)
pv_terminal = terminal_value / (1 + wacc) ** projection_years
sum_pv_fcfs = sum(pv_fcfs)
enterprise_value = sum_pv_fcfs + pv_terminal
equity_value = enterprise_value - debt_input + cash_input
intrinsic_per_share = equity_value / shares_input if shares_input else float("nan")
upside = (intrinsic_per_share - current_price) / current_price if current_price else 0
verdict = "under" if upside > 0 else "over"

# =============================================================================
# Tabbed layout
# =============================================================================
tab_overview, tab_assumptions, tab_dcf, tab_results, tab_sensitivity = st.tabs(
    [":bar_chart: Overview", ":clipboard: Assumptions", ":construction: DCF Build", ":dart: Results", ":thermometer: Sensitivity"]
)

# -----------------------------------------------------------------------------
# OVERVIEW TAB
# -----------------------------------------------------------------------------
with tab_overview:
    st.markdown(f"## {company_name}  &nbsp;`{ticker_input}`")
    st.caption(f"{sector} - {industry}")

    # Company description from Yahoo Finance
    if business_summary:
        st.markdown(
            f'<div class="company-desc">{business_summary}</div>',
            unsafe_allow_html=True,
        )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f'<div class="snap-card"><div class="label">Current Price</div>'
            f'<div class="value">${current_price:,.2f}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="snap-card"><div class="label">Market Cap</div>'
            f'<div class="value">${market_cap/1e9:,.1f}B</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="snap-card"><div class="label">Beta</div>'
            f'<div class="value">{beta:.2f}</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f'<div class="snap-card"><div class="label">Shares Out (M)</div>'
            f'<div class="value">{shares_out/1e6:,.0f}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-head">Historical Snapshot</div>', unsafe_allow_html=True)
    st.caption("Use this to ground your assumptions. Defaults in the sidebar are seeded from this history.")

    if hist_revenue is not None and len(hist_revenue) > 0:
        hist_df = pd.DataFrame({"Revenue ($M)": hist_revenue.round(0)})
        if hist_ebit is not None:
            hist_df["EBIT ($M)"] = hist_ebit.round(0)
            margins = (hist_ebit / hist_revenue.reindex(hist_ebit.index))
            hist_df["EBIT Margin"] = margins.map(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
        hist_df.index = [str(d.year) for d in hist_df.index]

        col_left, col_right = st.columns([3, 2])
        with col_left:
            st.dataframe(hist_df, use_container_width=True)
        with col_right:
            if hist_growth_default is not None:
                st.metric("Historical Revenue CAGR", f"{hist_growth_default:.1%}")
            if avg_margin_default is not None:
                st.metric("Average EBIT Margin", f"{avg_margin_default:.1%}")

        # Plotly bar chart of historical revenue
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[str(d.year) for d in hist_revenue.index],
            y=hist_revenue.values,
            marker_color="#2e7dd1",
            name="Revenue",
            text=[f"${v/1000:,.1f}B" if v >= 1000 else f"${v:,.0f}M" for v in hist_revenue.values],
            textposition="outside",
            textfont=dict(color="#0a2540"),
        ))
        fig.update_layout(
            title=dict(text="Historical Revenue", font=dict(color="#0a2540", size=16)),
            height=320,
            margin=dict(l=10, r=10, t=50, b=20),
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(gridcolor="#e5e7eb", color="#0a2540", title="$M"),
            xaxis=dict(color="#0a2540"),
            font=dict(color="#0a2540"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not load historical financials for this ticker.")

# -----------------------------------------------------------------------------
# ASSUMPTIONS TAB
# -----------------------------------------------------------------------------
with tab_assumptions:
    st.markdown('<div class="section-head">Your Current Inputs</div>', unsafe_allow_html=True)
    st.caption("Edit any of these in the sidebar. The model recomputes instantly.")

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("**Operating Assumptions**")
        op_df = pd.DataFrame({
            "Input": [
                "Base year revenue", "Revenue growth", "EBIT margin",
                "Effective tax rate", "Reinvestment rate", "Projection years",
            ],
            "Value": [
                f"${base_revenue:,.1f}M", f"{growth_rate:.2%}", f"{ebit_margin:.2%}",
                f"{tax_rate:.2%}", f"{reinvest_rate:.2%}", f"{projection_years} years",
            ],
        })
        st.dataframe(op_df, use_container_width=True, hide_index=True)

    with a2:
        st.markdown("**Discount Rate (WACC) Build-Up**")
        wacc_df = pd.DataFrame({
            "Component": [
                "Risk-free rate (Rf)", "Beta", "Equity risk premium (ERP)",
                "Cost of equity = Rf + Beta x ERP",
                "Pre-tax cost of debt (Kd)", "After-tax cost of debt = Kd x (1-t)",
                "Equity weight", "Debt weight", "WACC",
            ],
            "Value": [
                f"{risk_free:.2%}", f"{beta:.2f}", f"{erp:.2%}",
                f"{cost_equity:.2%}",
                f"{pretax_cost_debt:.2%}", f"{after_tax_cost_debt:.2%}",
                f"{equity_weight:.2%}", f"{debt_weight:.2%}", f"{wacc:.2%}",
            ],
        })
        st.dataframe(wacc_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-head">Terminal Value & Equity Bridge Inputs</div>', unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    with t1:
        st.metric("Terminal growth rate", f"{terminal_growth:.2%}")
        st.caption("Long-run sustainable growth. Should not exceed long-run GDP growth (~2-3%).")
    with t2:
        bridge_df = pd.DataFrame({
            "Item": ["Total debt", "Cash & equivalents", "Shares outstanding"],
            "Value": [f"${debt_input:,.1f}M", f"${cash_input:,.1f}M", f"{shares_input:,.1f}M"],
        })
        st.dataframe(bridge_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# DCF BUILD TAB
# -----------------------------------------------------------------------------
with tab_dcf:
    st.markdown('<div class="section-head">Year-by-Year Free Cash Flow Projection</div>', unsafe_allow_html=True)
    st.caption("Each row applies the formula: FCF = Revenue x EBIT margin x (1-tax) - Reinvestment, then discounted at WACC.")

    proj_df = pd.DataFrame({
        "Year": years,
        "Revenue ($M)": [round(x, 1) for x in revenues],
        "EBIT ($M)": [round(x, 1) for x in ebits],
        "NOPAT ($M)": [round(x, 1) for x in nopats],
        "Reinvestment ($M)": [round(x, 1) for x in reinvestments],
        "FCF ($M)": [round(x, 1) for x in fcfs],
        "Discount Factor": [round(x, 4) for x in discount_factors],
        "PV of FCF ($M)": [round(x, 1) for x in pv_fcfs],
    })
    st.dataframe(proj_df, use_container_width=True, hide_index=True)

    # FCF chart with Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years, y=fcfs, name="Nominal FCF",
        marker_color="#2e7dd1",
        text=[f"${v:,.0f}M" for v in fcfs], textposition="outside",
        textfont=dict(color="#0a2540"),
    ))
    fig.add_trace(go.Bar(
        x=years, y=pv_fcfs, name="PV of FCF",
        marker_color="#10b981",
        text=[f"${v:,.0f}M" for v in pv_fcfs], textposition="outside",
        textfont=dict(color="#0a2540"),
    ))
    fig.update_layout(
        title=dict(text="Projected Free Cash Flow vs. Present Value", font=dict(color="#0a2540", size=16)),
        barmode="group", height=400,
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=20),
        yaxis=dict(gridcolor="#e5e7eb", title="$M", color="#0a2540"),
        xaxis=dict(title="Year", color="#0a2540"),
        legend=dict(orientation="h", y=-0.18, font=dict(color="#0a2540")),
        font=dict(color="#0a2540"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-head">Terminal Value & Enterprise Value</div>', unsafe_allow_html=True)
    tv_df = pd.DataFrame({
        "Item": [
            f"FCF in Year {projection_years}",
            "Terminal FCF (Year N+1)",
            "Terminal Value (Gordon Growth)",
            "PV of Terminal Value",
            "Sum of PV of explicit FCFs",
            "Enterprise Value",
        ],
        "Value ($M)": [
            f"{fcfs[-1]:,.1f}", f"{terminal_fcf:,.1f}", f"{terminal_value:,.1f}",
            f"{pv_terminal:,.1f}", f"{sum_pv_fcfs:,.1f}", f"{enterprise_value:,.1f}",
        ],
        "Formula": [
            "From projection above",
            f"FCF_N x (1 + g) = {fcfs[-1]:,.1f} x (1 + {terminal_growth:.2%})",
            f"FCF_N+1 / (WACC - g) = {terminal_fcf:,.1f} / ({wacc:.2%} - {terminal_growth:.2%})",
            f"TV / (1 + WACC)^N",
            "Sum of PV column above",
            "PV of FCFs + PV of Terminal Value",
        ],
    })
    st.dataframe(tv_df, use_container_width=True, hide_index=True)

    # Composition donut
    fig2 = go.Figure(data=[go.Pie(
        labels=["PV of Explicit FCFs", "PV of Terminal Value"],
        values=[sum_pv_fcfs, pv_terminal],
        marker_colors=["#2e7dd1", "#f59e0b"],
        hole=0.5,
        textinfo="label+percent",
        textfont=dict(color="#0a2540", size=13),
    )])
    fig2.update_layout(
        title=dict(text="What's Driving the Enterprise Value?", font=dict(color="#0a2540", size=16)),
        height=340, margin=dict(l=10, r=10, t=50, b=20),
        showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#0a2540"),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Most DCFs are dominated by terminal value (often 60-80%), so your terminal assumptions matter a lot.")

# -----------------------------------------------------------------------------
# RESULTS TAB
# -----------------------------------------------------------------------------
with tab_results:
    st.markdown('<div class="section-head">Equity Bridge</div>', unsafe_allow_html=True)
    bridge_df = pd.DataFrame({
        "Item": [
            "Enterprise Value", "Less: Total Debt", "Plus: Cash & Equivalents",
            "Equity Value", "Shares Outstanding (M)", "Intrinsic Value per Share",
        ],
        "Value": [
            f"${enterprise_value:,.1f}M", f"${debt_input:,.1f}M", f"${cash_input:,.1f}M",
            f"${equity_value:,.1f}M", f"{shares_input:,.1f}", f"${intrinsic_per_share:,.2f}",
        ],
    })
    st.dataframe(bridge_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-head">Intrinsic Value vs. Market Price</div>', unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(
            f'<div class="result-card intrinsic">'
            f'<div class="rc-label">Intrinsic Value</div>'
            f'<div class="rc-value">${intrinsic_per_share:,.2f}</div>'
            f'<div class="rc-label">per share</div></div>',
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            f'<div class="result-card market">'
            f'<div class="rc-label">Market Price</div>'
            f'<div class="rc-value">${current_price:,.2f}</div>'
            f'<div class="rc-label">per share</div></div>',
            unsafe_allow_html=True,
        )
    with r3:
        gap = intrinsic_per_share - current_price
        label_text = "Undervalued" if upside > 0 else "Overvalued"
        st.markdown(
            f'<div class="result-card {verdict}">'
            f'<div class="rc-label">{label_text} by</div>'
            f'<div class="rc-value">{upside:+.1%}</div>'
            f'<div class="rc-label">${gap:+,.2f} / share</div></div>',
            unsafe_allow_html=True,
        )

    # Gauge chart for the headline verdict
    gauge_max = 100
    gauge_value = max(min(upside * 100, gauge_max), -gauge_max)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gauge_value,
        number={"suffix": "%", "font": {"size": 36, "color": "#0a2540"}},
        title={"text": "Implied Mispricing<br><span style='font-size:0.85em;color:#6b7280'>(positive = undervalued)</span>",
               "font": {"color": "#0a2540", "size": 16}},
        gauge={
            "axis": {"range": [-gauge_max, gauge_max], "tickwidth": 1, "tickcolor": "#0a2540", "tickfont": {"color": "#0a2540"}},
            "bar": {"color": "#10b981" if upside > 0 else "#ef4444"},
            "bgcolor": "white",
            "steps": [
                {"range": [-100, -25], "color": "#fee2e2"},
                {"range": [-25, 0], "color": "#fef3c7"},
                {"range": [0, 25], "color": "#fef3c7"},
                {"range": [25, 100], "color": "#d1fae5"},
            ],
            "threshold": {
                "line": {"color": "#0a2540", "width": 3},
                "thickness": 0.75, "value": gauge_value,
            },
        },
    ))
    fig_gauge.update_layout(
        height=340, margin=dict(l=20, r=20, t=70, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#0a2540"),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown('<div class="section-head">Download for Excel Replication</div>', unsafe_allow_html=True)
    st.caption("Use this to rebuild the same valuation in Excel for your validation submission.")
    csv_buffer = proj_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        ":arrow_down: Download projection (CSV)",
        data=csv_buffer,
        file_name=f"{ticker_input}_dcf_projection.csv",
        mime="text/csv",
    )

# -----------------------------------------------------------------------------
# SENSITIVITY TAB
# -----------------------------------------------------------------------------
with tab_sensitivity:
    st.markdown('<div class="section-head">Two-Way Sensitivity: Intrinsic Value per Share</div>', unsafe_allow_html=True)
    st.caption("Shows how the per-share intrinsic value moves when WACC and terminal growth change. Heatmap colors highlight where the stock looks cheap (green) vs. expensive (red) relative to today's market price.")

    wacc_range = np.linspace(max(wacc - 0.02, 0.04), wacc + 0.02, 7)
    g_range = np.linspace(max(terminal_growth - 0.015, 0.0), terminal_growth + 0.015, 7)

    sens = np.zeros((len(wacc_range), len(g_range)))
    for i, w in enumerate(wacc_range):
        for j, g in enumerate(g_range):
            if g >= w:
                sens[i, j] = np.nan
                continue
            pv_sum = sum(fcf / (1 + w) ** t for t, fcf in zip(years, fcfs))
            tv = fcfs[-1] * (1 + g) / (w - g)
            pv_tv = tv / (1 + w) ** projection_years
            ev = pv_sum + pv_tv
            eq = ev - debt_input + cash_input
            sens[i, j] = eq / shares_input if shares_input else np.nan

    pct_diff = (sens - current_price) / current_price * 100
    fig_heat = go.Figure(data=go.Heatmap(
        z=pct_diff,
        x=[f"{g:.2%}" for g in g_range],
        y=[f"{w:.2%}" for w in wacc_range],
        text=[[f"${v:,.2f}" if not np.isnan(v) else "" for v in row] for row in sens],
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#0a2540"},
        colorscale=[
            [0.0, "#b91c1c"], [0.4, "#fee2e2"], [0.5, "#ffffff"],
            [0.6, "#d1fae5"], [1.0, "#047857"],
        ],
        zmid=0,
        colorbar=dict(title=dict(text="% vs Market", font=dict(color="#0a2540")),
                      tickfont=dict(color="#0a2540")),
    ))
    fig_heat.update_layout(
        title=dict(text="Intrinsic value per share (color = % over/undervalued vs market)",
                   font=dict(color="#0a2540", size=15)),
        xaxis=dict(title="Terminal Growth Rate", color="#0a2540"),
        yaxis=dict(title="WACC", color="#0a2540"),
        height=460,
        margin=dict(l=10, r=10, t=60, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(color="#0a2540"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown('<div class="section-head">One-Way Sensitivity: Revenue Growth</div>', unsafe_allow_html=True)
    growth_range = np.linspace(max(growth_rate - 0.05, -0.05), growth_rate + 0.05, 11)
    growth_values = []
    for g in growth_range:
        rev_temp = base_revenue
        fcfs_temp = []
        for t in years:
            rev_temp = rev_temp * (1 + g)
            fcfs_temp.append(rev_temp * ebit_margin * (1 - tax_rate) * (1 - reinvest_rate))
        pv_sum = sum(f / (1 + wacc) ** t for t, f in zip(years, fcfs_temp))
        tv = fcfs_temp[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        pv_tv = tv / (1 + wacc) ** projection_years
        ev = pv_sum + pv_tv
        eq = ev - debt_input + cash_input
        growth_values.append(eq / shares_input)

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=[g * 100 for g in growth_range],
        y=growth_values,
        mode="lines+markers",
        line=dict(color="#2e7dd1", width=3),
        marker=dict(size=10, color="#1e4d8b"),
        name="Intrinsic Value",
    ))
    fig_line.add_hline(
        y=current_price, line_dash="dash", line_color="#ef4444", line_width=2,
        annotation_text=f"Market price ${current_price:,.2f}",
        annotation_position="top right",
        annotation_font=dict(color="#b91c1c"),
    )
    fig_line.update_layout(
        title=dict(text="How does intrinsic value change with revenue growth?",
                   font=dict(color="#0a2540", size=15)),
        xaxis=dict(title="Revenue Growth Rate (%)", gridcolor="#e5e7eb", color="#0a2540"),
        yaxis=dict(title="Intrinsic Value per Share ($)", gridcolor="#e5e7eb", color="#0a2540"),
        height=400,
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=20),
        font=dict(color="#0a2540"),
        showlegend=False,
    )
    st.plotly_chart(fig_line, use_container_width=True)

# =============================================================================
# Methodology + Footer
# =============================================================================
with st.expander(":books: Methodology Notes"):
    st.markdown(
        """
        **Free Cash Flow to the Firm (FCFF):**
        `FCFF = Revenue x EBIT margin x (1 - tax rate) x (1 - reinvestment rate)`

        **WACC** uses CAPM for the cost of equity:
        `Ke = Rf + Beta x ERP`
        `WACC = (E / (D+E)) x Ke + (D / (D+E)) x Kd x (1 - t)`

        **Terminal Value** (Gordon Growth):
        `TV = FCF_N x (1 + g) / (WACC - g)`

        **Equity Bridge:** Enterprise Value - Debt + Cash = Equity Value, divided by diluted shares.

        Data is pulled live from Yahoo Finance via the `yfinance` package and cached for one hour.
        """
    )

st.markdown(
    """
    <div class="app-footer">
        <div class="footer-title">DCF Equity Valuation App &nbsp;-&nbsp; FINA 4011/5011 - Project 2</div>
        <div class="footer-desc">
            A polished, color-coded Streamlit app that pulls live financials from Yahoo Finance
            for any ticker, lets the user override every assumption, and walks through the full
            DCF in a tabbed layout.
        </div>
        <div class="footer-team">
            <div class="team-label">Team Members</div>
            <div class="team-names">Kristian Blagoev &nbsp;&nbsp;&middot;&nbsp;&nbsp; Dom Dazzo &nbsp;&nbsp;&middot;&nbsp;&nbsp; Andrew Kohlbrenner</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)