import pandas as pd
from Modules import loader
from Modules.loader import add_to_issues_list




def remove_missing_cashier_id(df, issues):

    missing = df["CashierID"].isna().sum()

    if missing:
        add_to_issues_list("Major","Cashiers",f"Removed {missing} rows with missing CashierID.",issues)

    return df.dropna(subset=["CashierID"])

def flag_quality(df):

    is_good = df["CashierName"].notna()
    df["DataQuality"] = is_good.map({True: "Good", False: "Bad"})
    return df
 
 
def log_bad_rows(df, issues):
    bad_rows = df[df["DataQuality"] == "Bad"]
    for _, row in bad_rows.iterrows():
        add_to_issues_list("Minor","Cashiers",f"Missing CashierName: {row['CashierID']}",issues)

 
 
def keep_best_duplicate(df, issues):

    df = df.sort_values("DataQuality", ascending=False)  
 
    duplicates = df[df.duplicated("CashierID", keep="first")]
    for cashier_id in duplicates["CashierID"]:
        add_to_issues_list("Minor","Cashiers",f"Removed duplicate cashier: {cashier_id}",issues)
 
    return df.drop_duplicates("CashierID", keep="first")
 
 
def clean_cashiers(df, issues):
    df = df.drop_duplicates()
    df = remove_missing_cashier_id(df,issues)
    df = flag_quality(df)
    df = keep_best_duplicate(df, issues)
    log_bad_rows(df, issues)
    return df




if __name__ == "__main__":
    df = loader.cashiers_df
    cashiers_issues = []

    df.info()
    cleaned_cashiers_df = clean_cashiers(df,cashiers_issues)
    cleaned_cashiers_df.info()

    for issue in cashiers_issues:
        print(issue)