import streamlit as st
from Dashboard.components.load_data import load_data
from Dashboard.components.charts import (
    loyalty_tier_chart,
    gender_distribution_chart,
    top_customers_chart,
)

st.title("Customers")

sales_df = load_data()

col1, col2 = st.columns(2)
col1.plotly_chart(loyalty_tier_chart(sales_df), width='stretch')
col2.plotly_chart(gender_distribution_chart(sales_df), width='stretch')

st.plotly_chart(top_customers_chart(sales_df), width='stretch')