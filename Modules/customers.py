import pandas as pd
import loader
import re
from loader import add_to_issues_list 

df = loader.customers_df
customers_issues = []

EGYPTIAN_PHONE_PATTERN = re.compile(r"^01\d{9}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_TIERS = {"gold": "Gold", "silver": "Silver", "not a member": "Not a Member"}


def remove_missing_customer_id(df, issues):

    missing = df["CustomerID"].isna().sum()

    if missing:
        add_to_issues_list("Major","Customers",f"Removed {missing} rows with missing CustomerID.",issues)

    return df.dropna(subset=["CustomerID"])

def fix_names(df):
    df["CustomerFirstName"] = df["CustomerFirstName"].str.title()
    df["CustomerLastName"] = df["CustomerLastName"].str.title()
    return df


def fix_loyalty_tier(df):
    df["LoyaltyTier"] = df["LoyaltyTier"].str.lower().map(VALID_TIERS)
    return df


def is_valid_phone(phone):
    return isinstance(phone, str) and bool(EGYPTIAN_PHONE_PATTERN.match(phone))


def is_valid_email(email):
    return isinstance(email, str) and bool(EMAIL_PATTERN.match(email))


def flag_quality(df):

    phone_ok = df["Phone"].apply(is_valid_phone)
    email_ok = df["Email"].apply(is_valid_email)
    tier_ok = df["LoyaltyTier"].notna()

    is_good = phone_ok & email_ok & tier_ok
    df["DataQuality"] = is_good.map({True: "Good", False: "Bad"})
    return df


def log_bad_rows(df, issues):

    bad_rows = df[df["DataQuality"] == "Bad"]
    for _, row in bad_rows.iterrows():
        if not is_valid_phone(row["Phone"]):
            add_to_issues_list("Minor","Customers",f"Bad phone: {row['CustomerID']} -> {row['Phone']}",issues)
        if not is_valid_email(row["Email"]):
            add_to_issues_list("Minor","Customers",f"Bad email: {row['CustomerID']} -> {row['Email']}",issues)
        if pd.isna(row["LoyaltyTier"]):
            add_to_issues_list("Minor","Customers",f"Invalid loyalty tier: {row['CustomerID']}",issues)



def keep_best_duplicate(df, issues):

    df = df.sort_values("DataQuality", ascending=False) 

    duplicates = df[df.duplicated("CustomerID", keep="first")]

    for customer_id in duplicates["CustomerID"]:
        add_to_issues_list("Minor","Customers",f"Removed duplicate customer: {customer_id}",issues)

    return df.drop_duplicates("CustomerID", keep="first")


def clean_customers(df, issues):
    df = df.drop_duplicates()
    df = remove_missing_customer_id(df, issues)
    df = fix_names(df)
    df = fix_loyalty_tier(df)
    df = flag_quality(df)
    df = keep_best_duplicate(df, issues)
    log_bad_rows(df, issues)
    return df

cleaned_customers_df  = clean_customers(loader.customers_df,customers_issues)
cleaned_customers_df.info()
for issue in customers_issues:
    print(issue)