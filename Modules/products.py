import pandas as pd
import loader
from loader import add_to_issues_list 


df = loader.products_df
products_issues = []


def remove_missing_product_id(df, issues):

    missing = df["ProductID"].isna().sum()

    if missing:
        add_to_issues_list("Major","Products",f"Removed {missing} rows with missing ProductID.",issues)

    return df.dropna(subset=["ProductID"])

def fix_product_nameing(df):
    df["ProductName"] = df["ProductName"].str.title()
    df["Category"] = df["Category"].str.title()
    df["Brand"] = df["Brand"].str.title()
    return df


def flag_quality(df):
    is_good = df["ProductName"].notna() & df["Category"].notna() & df["Brand"].notna()
    df["DataQuality"] = is_good.map({True: "Good", False: "Bad"})
    return df
 
 
def log_bad_rows(df, issues):

    bad_rows = df[df["DataQuality"] == "Bad"]
    for _, row in bad_rows.iterrows():
        if pd.isna(row["ProductName"]):
            add_to_issues_list("Minor","Products",f"Missing ProductName: {row['ProductID']}",issues)
        if pd.isna(row["Category"]):
            add_to_issues_list("Minor","Products",f"Missing Category: {row['ProductID']}",issues)
        if pd.isna(row["Brand"]):
            add_to_issues_list("Minor","Products",f"Missing Brand: {row['ProductID']}",issues)
 
 
def keep_best_duplicate(df, issues):
    df = df.sort_values("DataQuality", ascending=False)  
 
    duplicates = df[df.duplicated("ProductID", keep="first")]
    for product_id in duplicates["ProductID"]:
        add_to_issues_list("Minor","Products",f"Removed duplicate product: {product_id}",issues)
 
    return df.drop_duplicates("ProductID", keep="first")
 
 
def clean_products(df, issues):
    df = df.drop_duplicates()
    df = remove_missing_product_id(df,issues)
    df = fix_product_nameing(df)
    df = flag_quality(df)
    df = keep_best_duplicate(df, issues)
    log_bad_rows(df, issues)
    return df

df.info()
cleaned_products_df = clean_products(df,products_issues)
cleaned_products_df.info()
for issue in products_issues:
    print(issue)