import re
import pandas as pd
from datetime import datetime
import loader

df = loader.transactions_df
transactions_issues = []

 
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y"]
TIME_PATTERN = re.compile(r"^([0-2]\d):[0-5]\d:[0-5]\d$")
 
VALID_PAYMENT_METHODS = {
    "cash": "Cash",
    "card": "Card",
    "credit card": "Card",
    "mobile wallet": "Mobile Wallet",
    "wallet": "Mobile Wallet",
    "voucher": "Voucher",
}
 
 
def trim_whitespace(df):
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].str.strip()
    return df
 
 
def remove_missing_transaction_id(df, issues):
    missing = df["TransactionID"].isna().sum()
    if missing:
        issues.append(f"Removed {missing} rows with missing TransactionID.")
    return df.dropna(subset=["TransactionID"])
 
 
def convert_types(df):
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["DiscountPercent"] = pd.to_numeric(df["DiscountPercent"], errors="coerce")
    return df
 
 
def standardize_payment_method(df):
    df["PaymentMethod"] = df["PaymentMethod"].str.lower().map(VALID_PAYMENT_METHODS)
    return df
 
 
def parse_date(value):
    if not isinstance(value, str):
        return None
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(value, date_format).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None
 
 
def standardize_dates(df):
    df["TransactionDate"] = df["TransactionDate"].apply(parse_date)
    return df
 
 
def remove_duplicate_transactions(df, issues):
    duplicates = df[df.duplicated("TransactionID", keep="first")]
    for transaction_id in duplicates["TransactionID"]:
        issues.append(f"Removed duplicate transaction: {transaction_id}")
    return df.drop_duplicates("TransactionID", keep="first")
 
 
def flag_quality(df):
    valid_product_id = df["ProductID"].notna()
    valid_branch_id = df["BranchID"].notna()
    valid_cashier_id = df["CashierID"].notna()

    valid_quantity = df["Quantity"].notna() & (df["Quantity"] > 0)
    valid_price = df["UnitPrice"].notna() & (df["UnitPrice"] > 0)
    valid_discount = df["DiscountPercent"].notna() & df["DiscountPercent"].between(0, 20)
    valid_date = df["TransactionDate"].notna()
    valid_time = df["TransactionTime"].apply(lambda t: isinstance(t, str) and bool(TIME_PATTERN.match(t)))
    valid_payment = df["PaymentMethod"].notna()
 

    is_good = valid_quantity & valid_price & valid_discount & valid_date & valid_time & valid_payment & valid_product_id & valid_branch_id & valid_cashier_id
    

    df["DataQuality"] = is_good.map({True: "Good", False: "Bad"})
    return df
 
 
def log_bad_rows(df, issues):
    bad_rows = df[df["DataQuality"] == "Bad"]
    for _, row in bad_rows.iterrows():
        transaction_id = row["TransactionID"]

        if pd.isna(row["CustomerID"]):
            issues.append(f"Missing CustomerID: {transaction_id}")
        if pd.isna(row["ProductID"]):
            issues.append(f"Missing ProductID: {transaction_id}")
        if pd.isna(row["BranchID"]):
            issues.append(f"Missing BranchID: {transaction_id}")
        if pd.isna(row["CashierID"]):
            issues.append(f"Missing CashierID: {transaction_id}")

        if pd.isna(row["PaymentMethod"]):
            issues.append(f"Invalid PaymentMethod: {transaction_id}")
        if pd.isna(row["Quantity"]) or row["Quantity"] <= 0:
            issues.append(f"Invalid Quantity: {transaction_id} -> {row['Quantity']}")
        if pd.isna(row["UnitPrice"]) or row["UnitPrice"] <= 0:
            issues.append(f"Invalid UnitPrice: {transaction_id} -> {row['UnitPrice']}")
        if pd.isna(row["DiscountPercent"]) or not (0 <= row["DiscountPercent"] <= 20):
            issues.append(f"Invalid DiscountPercent: {transaction_id} -> {row['DiscountPercent']}")
        if pd.isna(row["TransactionDate"]):
            issues.append(f"Unparseable TransactionDate: {transaction_id}")
        if not (isinstance(row["TransactionTime"], str) and TIME_PATTERN.match(row["TransactionTime"])):
            issues.append(f"Invalid TransactionTime: {transaction_id} -> {row['TransactionTime']}")
        if pd.isna(row["PaymentMethod"]):
            issues.append(f"Invalid PaymentMethod: {transaction_id}")
 
 
def clean_transactions(df, issues):
    df = trim_whitespace(df)
    df = remove_missing_transaction_id(df, issues)
    df = convert_types(df)
    df = standardize_payment_method(df)
    df = standardize_dates(df)
    df = remove_duplicate_transactions(df, issues)
    df = flag_quality(df)
    log_bad_rows(df, issues)
    return df

df.info()
cleaned_transactions_df = clean_transactions(df,transactions_issues)
cleaned_transactions_df.info()


for issue in transactions_issues:
    print(issue)