import pandas as pd
import loader


df = loader.branchs_df
branchs_issues = []
 
def check_single_branch_id(df, issues):

    branch_ids = df["BranchID"].dropna().unique()
 
    if len(branch_ids) == 0:
        issues.append("No valid BranchID found in file")
    elif len(branch_ids) > 1:
        issues.append(f"File contains multiple BranchIDs: {list(branch_ids)}")
 
def find_most_recurring_branch(df):
    result = (
    df.groupby(["BranchID", "BranchName", "BranchCity"])
      .size()
      .sort_values(ascending=False)
    )

    branch = result.index[0]

    return pd.DataFrame(
        [branch],
        columns=["BranchID", "BranchName", "BranchCity"]
    )


def clean_branches(df, issues):
    check_single_branch_id(df, issues)
    df = find_most_recurring_branch(df)
    return df


cleaned_df = clean_branches(df,branchs_issues)
print(cleaned_df.head())
for issue in branchs_issues:
    print(issue)