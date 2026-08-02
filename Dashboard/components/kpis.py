import streamlit as st
 
 
def total_revenue(df):
    return df["Revenue"].sum()
 
 
def total_transactions(df):
    return df["TransactionID"].nunique()
 
 
def total_customers(df):
    return df["CustomerID"].nunique()
 
 
def average_order_value(df):
    transactions = total_transactions(df)
    if transactions == 0:
        return 0
    return total_revenue(df) / transactions
 
 
def top_branch_by_revenue(df):
    if df.empty:
        return None
    revenue_by_branch = df.groupby("BranchName")["Revenue"].sum()
    return revenue_by_branch.idxmax()
 
 
def render_kpi_row(df):
    col1, col2, col3, col4 = st.columns(4)
 
    col1.metric("Total Revenue", f"${total_revenue(df):,.2f}")
    col2.metric("Total Transactions", f"{total_transactions(df):,}")
    col3.metric("Total Customers", f"{total_customers(df):,}")
    col4.metric("Average Order Value", f"${average_order_value(df):,.2f}")
