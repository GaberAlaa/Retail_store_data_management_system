import pandas as pd
import loader


df = loader.branchs_df
branchs_issues = []

print(df.head())


def trim_whitespace(df):
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].str.strip()
    return df
 
 
def check_single_branch_id(df, issues):

    branch_ids = df["BranchID"].dropna().unique()
 
    if len(branch_ids) == 0:
        issues.append("No valid BranchID found in file")
    elif len(branch_ids) > 1:
        issues.append(f"File contains multiple BranchIDs: {list(branch_ids)}")
 
 
def first_non_blank(column):
    non_blank = column.dropna()
    return non_blank.iloc[0] if len(non_blank) > 0 else None
 
 
def collapse_to_one_branch(df, issues):

    branch_id = first_non_blank(df["BranchID"])
    branch_name = first_non_blank(df["BranchName"])
    branch_city = first_non_blank(df["BranchCity"])
 
    if df["BranchName"].nunique() > 1:
        issues.append("Conflicting BranchName values found")
    if df["BranchCity"].nunique() > 1:
        issues.append("Conflicting BranchCity values found")
 
    if branch_name is None:
        issues.append(f"BranchName missing for {branch_id}")
    if branch_city is None:
        issues.append(f"BranchCity missing for {branch_id}")
 
    return pd.DataFrame([{
        "BranchID": branch_id,
        "BranchName": branch_name,
        "BranchCity": branch_city,
    }])
 
 
def clean_branches(df, issues):
    df = trim_whitespace(df)
    check_single_branch_id(df, issues)
    df = collapse_to_one_branch(df, issues)
    return df
