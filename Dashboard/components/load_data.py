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

    transactions.columns = [
        "TransactionID",
        "CustomerID",
        "ProductID",
        "BranchID",
        "CashierID",
        "Quantity",
        "UnitPrice",
        "DiscountPercent",
        "PaymentMethod",
        "TransactionTime",
        "TransactionDate"
    ]
    products.columns = [
        "ProductID",
        "ProductName",
        "Category",
        "Brand"
    ]
    customers.columns = [
        "CustomerID",
        "CustomerFirstName",
        "CustomerLastName",
        "Gender",
        "Phone",
        "Email",
        "LoyaltyTier"
    ]
    branches.columns = [
        "BranchID",
        "BranchName",
        "BranchCity"
    ]
    cashiers.columns = [
        "CashierID",
        "CashierName"
    ]
    transactions["Quantity"] = pd.to_numeric(transactions["Quantity"], errors="coerce")
    transactions["UnitPrice"] = pd.to_numeric(transactions["UnitPrice"], errors="coerce")
    transactions["DiscountPercent"] = pd.to_numeric(transactions["DiscountPercent"], errors="coerce")

    sales = (
    transactions
    .merge(products, on="ProductID")
    .merge(customers, on="CustomerID")
    .merge(branches, on="BranchID")
    .merge(cashiers, on="CashierID")
)

    sales["TransactionDate"] = pd.to_datetime(sales["TransactionDate"])
    sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"] * (1 - sales["DiscountPercent"] / 100)


    return sales
