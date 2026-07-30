import pandas as pd
import numpy as np
import shutil
from pathlib import Path
from config import INCOMING_FOLDER ,RAW_FOLDER

file_path = INCOMING_FOLDER/"BR01_2026-07-22.csv"

def divied_into_dfs(df : pd.DataFrame):
    transactions_df = df[["TransactionID", "CustomerID", "ProductID", "BranchID","CashierID","Quantity","UnitPrice","DiscountPercent","PaymentMethod","TransactionTime","TransactionDate"]]
    customers_df = df[["CustomerID", "CustomerFirstName", "CustomerLastName","Gender","Phone","Email","LoyaltyTier"]]
    branchs_df = df[["BranchID", "BranchName", "BranchCity"]]
    products_df = df[["ProductID", "ProductName", "Category","Brand"]]
    cashiers_df = df[["CashierID", "CashierName"]]
    return transactions_df,customers_df,branchs_df,products_df,cashiers_df

def read_branch_csv(path :Path):
    return pd.read_csv(path,dtype=str)

 
def copy_to_raw(file_path: Path) -> Path:
    destination = RAW_FOLDER / file_path.name
    shutil.copy(file_path, destination)

def trim_whitespace(df):
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].str.strip()
    return df

def add_to_issues_list(status, table, string, issues_list):
    issues_list.append({"status": status, "table": table, "message": string})

full_df = read_branch_csv(file_path)
full_df = trim_whitespace(full_df)
copy_to_raw(file_path)
transactions_df,customers_df,branchs_df,products_df,cashiers_df = divied_into_dfs(full_df)