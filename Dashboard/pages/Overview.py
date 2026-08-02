import streamlit as st
from Dashboard.components.load_data import load_data
from Dashboard.components.kpis import render_kpi_row
from Dashboard.components.charts import revenue_over_time_chart, revenue_by_branch_chart

st.title("Overview")

sales_df = load_data()


st.plotly_chart(revenue_over_time_chart(sales_df), width='stretch')
st.plotly_chart(revenue_by_branch_chart(sales_df), width='stretch')