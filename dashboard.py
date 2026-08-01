from Modules.DBconnection import get_connection
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    engine = get_connection()
    transactions = pd.read_sql("SELECT * FROM Transactions", engine)
    products = pd.read_sql("SELECT * FROM Products", engine)
    customers = pd.read_sql("SELECT * FROM Customers", engine)
    branches = pd.read_sql("SELECT * FROM Branches", engine)
    cashiers = pd.read_sql("SELECT * FROM Cashiers", engine)
    return transactions, products, customers, branches, cashiers

load_data()

st.write("hello world")