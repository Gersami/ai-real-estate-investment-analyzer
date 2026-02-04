import streamlit as st
import numpy_financial as npf

st.set_page_config(page_title="AI Real Estate Investment Analyzer", layout="wide")
st.title("AI Real Estate Investment Analyzer")

st.sidebar.header("Property")

price = st.sidebar.number_input("Purchase Price", value=150000)
renovation = st.sidebar.number_input("Renovation Cost", value=15000)
legal = st.sidebar.number_input("Closing / Legal Costs", value=3000)

st.sidebar.header("Rental")
rent = st.sidebar.number_input("Monthly Rent", value=1200)
vacancy = st.sidebar.slider("Vacancy %", 0, 30, 5)
expenses = st.sidebar.number_input("Monthly Operating Expenses", value=250)

st.sidebar.header("Financing")
down_pct = st.sidebar.slider("Down Payment %", 0, 100, 30)
interest = st.sidebar.number_input("Loan Rate %", value=9.5)
years = st.sidebar.number_input("Loan Term (years)", value=10)

st.sidebar.header("Exit")
appreciation = st.sidebar.slider("Annual Appreciation %", 0, 15, 5)
hold_years = st.sidebar.number_input("Hold Period (years)", value=5)

# ---------------- CALCULATIONS ----------------

total_cost = price + renovation + legal
down_payment = total_cost * down_pct / 100
loan = total_cost - down_payment

monthly_rate = (interest/100)/12
months = years * 12
mortgage = npf.pmt(monthly_rate, months, -loan)

effective_rent = rent * (1 - vacancy/100)
monthly_cashflow = effective_rent - expenses - mortgage

# Annual CF list for IRR
annual_cf = [monthly_cashflow*12]*hold_years

# Exit calculations
future_price = price * ((1 + appreciation/100) ** hold_years)

remaining_balance = npf.fv(monthly_rate, hold_years*12, mortgage, -loan)

sale_costs = future_price * 0.03
net_sale = future_price - remaining_balance - sale_costs

annual_cf[-1] += net_sale

irr = npf.irr([-down_payment] + annual_cf)

roi = (sum(annual_cf) - down_payment) / down_payment

# ---------------- UI ----------------

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Cashflow", f"${monthly_cashflow:,.0f}")
col2.metric("Mortgage Payment", f"${mortgage:,.0f}")
col3.metric("Net Sale Proceeds", f"${net_sale:,.0f}")
col4.metric("IRR", f"{irr*100:.2f}%")

st.subheader("Cashflow Over Hold Period")
st.bar_chart(annual_cf)

st.subheader("AI Investment Insight")

if monthly_cashflow < 0:
    st.warning("Negative cashflow property. Investment depends on appreciation.")
elif irr > 0.15:
    st.success("Strong investment profile with high IRR.")
else:
    st.info("Moderate return profile with balanced risk.")
