import streamlit as st
from Dashboard.components.load_data import load_data
from Dashboard.components.charts import (
    category_revenue_chart,
    top_products_chart,
    payment_method_chart,
)

st.title("Sales")

sales_df = load_data()

branches = ["All"] + sorted(sales_df["BranchName"].dropna().unique().tolist())
selected_branch = st.sidebar.selectbox("Branch", branches)

if selected_branch != "All":
    sales_df = sales_df[sales_df["BranchName"] == selected_branch]

col1, col2 = st.columns(2)
col1.plotly_chart(category_revenue_chart(sales_df), width='stretch')
col2.plotly_chart(payment_method_chart(sales_df), width='stretch')

st.plotly_chart(top_products_chart(sales_df), width='stretch')