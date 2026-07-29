import pandas as pd
import loader


df = loader.cashiers_df
cashiers_issues = []


def remove_missing_cashier_id(df, issues):

    missing = df["CashierID"].isna().sum()

    if missing:
        issues.append(f"Removed {missing} rows with missing CashierID.")

    return df.dropna(subset=["CashierID"])

def flag_quality(df):

    is_good = df["CashierName"].notna()
    df["DataQuality"] = is_good.map({True: "Good", False: "Bad"})
    return df
 
 
def log_bad_rows(df, issues):
    bad_rows = df[df["DataQuality"] == "Bad"]
    for _, row in bad_rows.iterrows():
        issues.append(f"Missing CashierName: {row['CashierID']}")
 
 
def keep_best_duplicate(df, issues):

    df = df.sort_values("DataQuality", ascending=False)  
 
    duplicates = df[df.duplicated("CashierID", keep="first")]
    for cashier_id in duplicates["CashierID"]:
        issues.append(f"Removed duplicate cashier: {cashier_id}")
 
    return df.drop_duplicates("CashierID", keep="first")
 
 
def clean_cashiers(df, issues):
    df = df.drop_duplicates()
    df = remove_missing_cashier_id(df,cashiers_issues)
    df = flag_quality(df)
    df = keep_best_duplicate(df, issues)
    log_bad_rows(df, issues)
    return df


df.info()

cleaned_cashiers_df = clean_cashiers(df,cashiers_issues)
cleaned_cashiers_df.info()

for issue in cashiers_issues:
    print(issue)