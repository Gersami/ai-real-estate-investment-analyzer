import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf

st.set_page_config(page_title="AI Real Estate Investment Analyzer", layout="wide")
st.title("AI Real Estate Investment Analyzer")
st.caption("MVP: ROI • Cashflow • Financing • Simple scenarios")

# ---- Sidebar inputs
with st.sidebar:
    st.header("Property")
    purchase_price = st.number_input("Purchase price", min_value=0.0, value=150000.0, step=1000.0)
    renovation_cost = st.number_input("Renovation cost", min_value=0.0, value=15000.0, step=500.0)
    closing_cost = st.number_input("Closing / legal costs", min_value=0.0, value=3000.0, step=100.0)

    st.header("Rental")
    monthly_rent = st.number_input("Monthly rent", min_value=0.0, value=1200.0, step=50.0)
    vacancy_pct = st.slider("Vacancy (%)", 0.0, 40.0, 5.0, 0.5)
    monthly_expenses = st.number_input("Monthly operating expenses", min_value=0.0, value=250.0, step=10.0)

    st.header("Financing")
    down_payment_pct = st.slider("Down payment (%)", 0.0, 100.0, 30.0, 1.0)
    loan_rate = st.number_input("Loan rate (APR %)", min_value=0.0, value=9.5, step=0.1)
    loan_years = st.number_input("Loan term (years)", min_value=1, value=10, step=1)

    st.header("Exit")
    appreciation_pct = st.number_input("Annual appreciation (%)", value=5.0, step=0.5)
    hold_years = st.number_input("Hold period (years)", min_value=1, value=5, step=1)

# ---- Calculations
total_cost = purchase_price + renovation_cost + closing_cost
down_payment = purchase_price * (down_payment_pct / 100.0)
loan_amount = max(purchase_price - down_payment, 0.0)

r = (loan_rate / 100.0) / 12.0
n = int(loan_years) * 12
mortgage_payment = npf.pmt(r, n, -loan_amount) if loan_amount > 0 else 0.0

effective_rent = monthly_rent * (1.0 - vacancy_pct / 100.0)
net_monthly_cashflow = effective_rent - monthly_expenses - mortgage_payment
net_annual_cashflow = net_monthly_cashflow * 12.0

future_sale_price = purchase_price * ((1.0 + appreciation_pct / 100.0) ** int(hold_years))

# very simple profit model (MVP): cashflows + future price - remaining debt (approx)
profit_est = (net_annual_cashflow * int(hold_years)) + (future_sale_price - loan_amount)
roi_pct = (profit_est / max(down_payment + renovation_cost + closing_cost, 1.0)) * 100.0

# ---- UI outputs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Net Monthly Cashflow", f"${net_monthly_cashflow:,.2f}")
c2.metric("Mortgage Payment", f"${mortgage_payment:,.2f}")
c3.metric("Future Sale Price", f"${future_sale_price:,.0f}")
c4.metric("ROI (rough) %", f"{roi_pct:,.2f}%")

st.subheader("Annual Cashflow (Hold Period)")
cashflow_df = pd.DataFrame({"Year": list(range(1, int(hold_years) + 1)),
                            "Annual Cashflow": [net_annual_cashflow] * int(hold_years)})
st.bar_chart(cashflow_df.set_index("Year"))

st.subheader("Sensitivity Scenarios (Quick)")
scenarios = []
for name, rent_mult, vac_add, rate_add in [
    ("Base", 1.0, 0.0, 0.0),
    ("Rent -10%", 0.9, 0.0, 0.0),
    ("Vacancy +5pp", 1.0, 5.0, 0.0),
    ("Rate +2pp", 1.0, 0.0, 2.0),
]:
    rr = monthly_rent * rent_mult
    vv = min(vacancy_pct + vac_add, 40.0)
    lr = loan_rate + rate_add

    r2 = (lr / 100.0) / 12.0
    mp2 = npf.pmt(r2, n, -loan_amount) if loan_amount > 0 else 0.0
    eff2 = rr * (1.0 - vv / 100.0)
    cf2 = eff2 - monthly_expenses - mp2

    scenarios.append({"Scenario": name, "Net Monthly Cashflow": round(cf2, 2), "Loan Rate %": lr, "Vacancy %": vv})

st.dataframe(pd.DataFrame(scenarios), use_container_width=True)
