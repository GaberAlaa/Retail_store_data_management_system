from Modules import loader,customers,products,branchs,cashiers,transactions,files,Database,logger
from Modules.loader import add_to_issues_list

 
def load_and_clean_file(file_path):
    issues = []
 
    full_df = loader.read_branch_csv(file_path)
    full_df = loader.trim_whitespace(full_df)
    files.copy_to_raw(file_path)
 
    transactions_df, customers_df, branchs_df, products_df, cashiers_df = loader.divied_into_dfs(full_df)
 
    cleaned_customers_df = customers.clean_customers(customers_df, issues)
    cleaned_products_df = products.clean_products(products_df, issues)
    cleaned_branches_df = branchs.clean_branches(branchs_df, issues)
    cleaned_cashiers_df = cashiers.clean_cashiers(cashiers_df, issues)
    cleaned_transactions_df = transactions.clean_transactions(transactions_df, issues)
 
    return (
        cleaned_transactions_df,
        cleaned_customers_df,
        cleaned_products_df,
        cleaned_branches_df,
        cleaned_cashiers_df,
        issues,
    )
 
 
def check_foreign_keys(transactions_df, customers_df, products_df, branches_df, cashiers_df, issues):
    valid_customer_ids = set(customers_df["CustomerID"])
    valid_product_ids = set(products_df["ProductID"])
    valid_branch_ids = set(branches_df["BranchID"])
    valid_cashier_ids = set(cashiers_df["CashierID"])
 
    bad_customer = ~transactions_df["CustomerID"].isin(valid_customer_ids)
    bad_product = ~transactions_df["ProductID"].isin(valid_product_ids)
    bad_branch = ~transactions_df["BranchID"].isin(valid_branch_ids)
    bad_cashier = ~transactions_df["CashierID"].isin(valid_cashier_ids)
 
    for transaction_id in transactions_df.loc[bad_customer, "TransactionID"]:
        add_to_issues_list("Major", "Transactions", f"Transaction {transaction_id} references a CustomerID not found in Customers table", issues)
    for transaction_id in transactions_df.loc[bad_product, "TransactionID"]:
        add_to_issues_list("Major", "Transactions", f"Transaction {transaction_id} references a ProductID not found in Products table", issues)
    for transaction_id in transactions_df.loc[bad_branch, "TransactionID"]:
        add_to_issues_list("Major", "Transactions", f"Transaction {transaction_id} references a BranchID not found in Branches table", issues)
    for transaction_id in transactions_df.loc[bad_cashier, "TransactionID"]:
        add_to_issues_list("Major", "Transactions", f"Transaction {transaction_id} references a CashierID not found in Cashiers table", issues)

def has_major_issues(issues):
    return any(issue["status"] == "Major" for issue in issues)
 
 
def decide_status(issues):
    return "Rejected" if has_major_issues(issues) else "Processed"
 
 
def process_file(file_path):
    (
        cleaned_transactions_df,
        cleaned_customers_df,
        cleaned_products_df,
        cleaned_branches_df,
        cleaned_cashiers_df,
        issues,
    ) = load_and_clean_file(file_path)
 
    check_foreign_keys(
        cleaned_transactions_df,
        cleaned_customers_df,
        cleaned_products_df,
        cleaned_branches_df,
        cleaned_cashiers_df,
        issues,
    )
 
    status = decide_status(issues)
 
    if status == "Processed":
        Database.write_to_database(
            cleaned_customers_df,
            cleaned_products_df,
            cleaned_branches_df,
            cleaned_cashiers_df,
            cleaned_transactions_df,
        )
        files.move_to_processed(file_path)
    else:
        files.move_to_rejected(file_path)
 
    logger.generate_log_file(status, file_path, issues)
 


if __name__ == "__main__":
    cleaned_transactions_df,cleaned_customers_df,cleaned_products_df,cleaned_branches_df,cleaned_cashiers_df,issues = load_and_clean_file(loader.file_path)
    check_foreign_keys(cleaned_transactions_df,cleaned_customers_df,cleaned_products_df,cleaned_branches_df,cleaned_cashiers_df,issues)
    for issue in issues:
        print(issue)