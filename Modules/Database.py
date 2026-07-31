import pandas as pd
from Modules import customers,products,cashiers,DBconnection
def existing_row_quality(existing_row, flag_quality_function):

    one_row_df = pd.DataFrame([existing_row])
    one_row_df = flag_quality_function(one_row_df)
    return one_row_df["DataQuality"].iloc[0]

# ========================================================================================================================
def get_existing_customer(cursor, customer_id):
    cursor.execute(
        "SELECT CustomerFirstName, CustomerLastName, Gender, Phone, Email, LoyaltyTier "
        "FROM Customers WHERE CustomerID = %s",
        (customer_id,),
    )
    row = cursor.fetchone()
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


def upsert_customer(cursor, row):
    existing = get_existing_customer(cursor, row["CustomerID"])

    if existing is not None:
        existing_quality = existing_row_quality(existing, customers.flag_quality)
        if existing_quality == "Good" and row["DataQuality"] == "Bad":
            return  

    query = """
        INSERT INTO Customers (CustomerID, CustomerFirstName, CustomerLastName, Gender, Phone, Email, LoyaltyTier)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (CustomerID) DO UPDATE SET
            CustomerFirstName = EXCLUDED.CustomerFirstName,
            CustomerLastName = EXCLUDED.CustomerLastName,
            Gender = EXCLUDED.Gender,
            Phone = EXCLUDED.Phone,
            Email = EXCLUDED.Email,
            LoyaltyTier = EXCLUDED.LoyaltyTier
    """
    cursor.execute(query, (
        row["CustomerID"], row["CustomerFirstName"], row["CustomerLastName"],
        row["Gender"], row["Phone"], row["Email"], row["LoyaltyTier"],
    ))

# ========================================================================================================================
def get_existing_product(cursor, product_id):
    cursor.execute(
        "SELECT ProductName, Category, Brand FROM Products WHERE ProductID = %s",
        (product_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {
        "ProductID": product_id,
        "ProductName": row[0],
        "Category": row[1],
        "Brand": row[2],
    }


def upsert_product(cursor, row):
    existing = get_existing_product(cursor, row["ProductID"])

    if existing is not None:
        existing_quality = existing_row_quality(existing, products.flag_quality)
        if existing_quality == "Good" and row["DataQuality"] == "Bad":
            return

    query = """
        INSERT INTO Products (ProductID, ProductName, Category, Brand)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ProductID) DO UPDATE SET
            ProductName = EXCLUDED.ProductName,
            Category = EXCLUDED.Category,
            Brand = EXCLUDED.Brand
    """
    cursor.execute(query, (row["ProductID"], row["ProductName"], row["Category"], row["Brand"]))
# ========================================================================================================================
def get_existing_cashier(cursor, cashier_id):
    cursor.execute(
        "SELECT CashierName FROM Cashiers WHERE CashierID = %s",
        (cashier_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {"CashierID": cashier_id, "CashierName": row[0]}


def upsert_cashier(cursor, row):
    existing = get_existing_cashier(cursor, row["CashierID"])

    if existing is not None:
        existing_quality = existing_row_quality(existing, cashiers.flag_quality)
        if existing_quality == "Good" and row["DataQuality"] == "Bad":
            return

    query = """
        INSERT INTO Cashiers (CashierID, CashierName)
        VALUES (%s, %s)
        ON CONFLICT (CashierID) DO UPDATE SET
            CashierName = EXCLUDED.CashierName
    """
    cursor.execute(query, (row["CashierID"], row["CashierName"]))
# ========================================================================================================================
def upsert_branch(cursor, row):
    query = """
        INSERT INTO Branches (BranchID, BranchName, BranchCity)
        VALUES (%s, %s, %s)
        ON CONFLICT (BranchID) DO UPDATE SET
            BranchName = EXCLUDED.BranchName,
            BranchCity = EXCLUDED.BranchCity
    """
    cursor.execute(query, (row["BranchID"], row["BranchName"], row["BranchCity"]))


# ========================================================================================================================
def insert_transaction(cursor, row):
    query = """
        INSERT INTO Transactions (
            TransactionID, CustomerID, ProductID, BranchID, CashierID,
            Quantity, UnitPrice, DiscountPercent, PaymentMethod,
            TransactionTime, TransactionDate
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (TransactionID) DO NOTHING
    """
    cursor.execute(query, (
        row["TransactionID"], row["CustomerID"], row["ProductID"], row["BranchID"], row["CashierID"],
        row["Quantity"], row["UnitPrice"], row["DiscountPercent"], row["PaymentMethod"],
        row["TransactionTime"], row["TransactionDate"],
    ))

def write_to_database(customers_df, products_df, branches_df, cashiers_df, transactions_df):

    with DBconnection.get_connection() as conn:
        with conn.cursor() as cursor:
            for _, row in customers_df.iterrows():
                upsert_customer(cursor, row)
            for _, row in products_df.iterrows():
                upsert_product(cursor, row)
            for _, row in branches_df.iterrows():
                upsert_branch(cursor, row)
            for _, row in cashiers_df.iterrows():
                upsert_cashier(cursor, row)
            for _, row in transactions_df.iterrows():
                insert_transaction(cursor, row)