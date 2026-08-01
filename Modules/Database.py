import pandas as pd
import sqlalchemy
from sqlalchemy import text
from Modules import customers, products, cashiers, DBconnection
 
 
def existing_row_quality(existing_row, flag_quality_function):
    one_row_df = pd.DataFrame([existing_row])
    one_row_df = flag_quality_function(one_row_df)
    return one_row_df["DataQuality"].iloc[0]
 
 
# ========================================================================================================================
def get_existing_customer(conn, customer_id):
    result = conn.execute(
        text(
            "SELECT CustomerFirstName, CustomerLastName, Gender, Phone, Email, LoyaltyTier "
            "FROM Customers WHERE CustomerID = :customer_id"
        ),
        {"customer_id": customer_id},
    )
    row = result.fetchone()
    if row is None:
        return None
    return {
        "CustomerID": customer_id,
        "CustomerFirstName": row[0],
        "CustomerLastName": row[1],
        "Gender": row[2],
        "Phone": row[3],
        "Email": row[4],
        "LoyaltyTier": row[5],
    }
 
 
def upsert_customer(conn, row):
    existing = get_existing_customer(conn, row["CustomerID"])
 
    if existing is not None:
        existing_quality = existing_row_quality(existing, customers.flag_quality)
        if existing_quality == "Good" and row["DataQuality"] == "Bad":
            return
 
    query = text("""
        INSERT INTO Customers (CustomerID, CustomerFirstName, CustomerLastName, Gender, Phone, Email, LoyaltyTier)
        VALUES (:customer_id, :first_name, :last_name, :gender, :phone, :email, :loyalty_tier)
        ON CONFLICT (CustomerID) DO UPDATE SET
            CustomerFirstName = EXCLUDED.CustomerFirstName,
            CustomerLastName = EXCLUDED.CustomerLastName,
            Gender = EXCLUDED.Gender,
            Phone = EXCLUDED.Phone,
            Email = EXCLUDED.Email,
            LoyaltyTier = EXCLUDED.LoyaltyTier
    """)
    conn.execute(query, {
        "customer_id": row["CustomerID"],
        "first_name": row["CustomerFirstName"],
        "last_name": row["CustomerLastName"],
        "gender": row["Gender"],
        "phone": row["Phone"],
        "email": row["Email"],
        "loyalty_tier": row["LoyaltyTier"],
    })
 
 
# ========================================================================================================================
def get_existing_product(conn, product_id):
    result = conn.execute(
        text("SELECT ProductName, Category, Brand FROM Products WHERE ProductID = :product_id"),
        {"product_id": product_id},
    )
    row = result.fetchone()
    if row is None:
        return None
    return {
        "ProductID": product_id,
        "ProductName": row[0],
        "Category": row[1],
        "Brand": row[2],
    }
 
 
def upsert_product(conn, row):
    existing = get_existing_product(conn, row["ProductID"])
 
    if existing is not None:
        existing_quality = existing_row_quality(existing, products.flag_quality)
        if existing_quality == "Good" and row["DataQuality"] == "Bad":
            return
 
    query = text("""
        INSERT INTO Products (ProductID, ProductName, Category, Brand)
        VALUES (:product_id, :product_name, :category, :brand)
        ON CONFLICT (ProductID) DO UPDATE SET
            ProductName = EXCLUDED.ProductName,
            Category = EXCLUDED.Category,
            Brand = EXCLUDED.Brand
    """)
    conn.execute(query, {
        "product_id": row["ProductID"],
        "product_name": row["ProductName"],
        "category": row["Category"],
        "brand": row["Brand"],
    })
 
 
# ========================================================================================================================
def get_existing_cashier(conn, cashier_id):
    result = conn.execute(
        text("SELECT CashierName FROM Cashiers WHERE CashierID = :cashier_id"),
        {"cashier_id": cashier_id},
    )
    row = result.fetchone()
    if row is None:
        return None
    return {"CashierID": cashier_id, "CashierName": row[0]}
 
 
def upsert_cashier(conn, row):
    existing = get_existing_cashier(conn, row["CashierID"])
 
    if existing is not None:
        existing_quality = existing_row_quality(existing, cashiers.flag_quality)
        if existing_quality == "Good" and row["DataQuality"] == "Bad":
            return
 
    query = text("""
        INSERT INTO Cashiers (CashierID, CashierName)
        VALUES (:cashier_id, :cashier_name)
        ON CONFLICT (CashierID) DO UPDATE SET
            CashierName = EXCLUDED.CashierName
    """)
    conn.execute(query, {
        "cashier_id": row["CashierID"],
        "cashier_name": row["CashierName"],
    })
 
 
# ========================================================================================================================
def upsert_branch(conn, row):
    query = text("""
        INSERT INTO Branches (BranchID, BranchName, BranchCity)
        VALUES (:branch_id, :branch_name, :branch_city)
        ON CONFLICT (BranchID) DO UPDATE SET
            BranchName = EXCLUDED.BranchName,
            BranchCity = EXCLUDED.BranchCity
    """)
    conn.execute(query, {
        "branch_id": row["BranchID"],
        "branch_name": row["BranchName"],
        "branch_city": row["BranchCity"],
    })
 
 
# ========================================================================================================================
def insert_transaction(conn, row):
    query = text("""
        INSERT INTO Transactions (
            TransactionID, CustomerID, ProductID, BranchID, CashierID,
            Quantity, UnitPrice, DiscountPercent, PaymentMethod,
            TransactionTime, TransactionDate
        )
        VALUES (
            :transaction_id, :customer_id, :product_id, :branch_id, :cashier_id,
            :quantity, :unit_price, :discount_percent, :payment_method,
            :transaction_time, :transaction_date
        )
        ON CONFLICT (TransactionID) DO NOTHING
    """)
    conn.execute(query, {
        "transaction_id": row["TransactionID"],
        "customer_id": row["CustomerID"],
        "product_id": row["ProductID"],
        "branch_id": row["BranchID"],
        "cashier_id": row["CashierID"],
        "quantity": row["Quantity"],
        "unit_price": row["UnitPrice"],
        "discount_percent": row["DiscountPercent"],
        "payment_method": row["PaymentMethod"],
        "transaction_time": row["TransactionTime"],
        "transaction_date": row["TransactionDate"],
    })
 
 
def write_to_database(customers_df, products_df, branches_df, cashiers_df, transactions_df):
    engine = DBconnection.get_connection()
 
    with engine.begin() as conn:
        for _, row in customers_df.iterrows():
            upsert_customer(conn, row)
        for _, row in products_df.iterrows():
            upsert_product(conn, row)
        for _, row in branches_df.iterrows():
            upsert_branch(conn, row)
        for _, row in cashiers_df.iterrows():
            upsert_cashier(conn, row)
        for _, row in transactions_df.iterrows():
            insert_transaction(conn, row)
