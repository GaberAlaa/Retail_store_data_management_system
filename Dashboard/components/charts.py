import pandas as pd
import plotly.express as px
import datetime as dt

def revenue_over_time_chart(df):
    daily = df.groupby("TransactionDate", as_index=False)["Revenue"].sum()
    fig = px.line(daily, x="TransactionDate", y="Revenue", title="Revenue Over Time")
    fig.update_layout(xaxis_title="Date", yaxis_title="Revenue")
    return fig


def revenue_by_branch_chart(df):
    by_branch = df.groupby("BranchName", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    fig = px.bar(by_branch, x="BranchName", y="Revenue", title="Revenue by Branch")
    fig.update_layout(xaxis_title="Branch", yaxis_title="Revenue")
    return fig


def category_revenue_chart(df):
    by_category = df.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    fig = px.bar(by_category, x="Category", y="Revenue", title="Revenue by Category")
    fig.update_layout(xaxis_title="Category", yaxis_title="Revenue")
    return fig


def top_products_chart(df, n=10):
    by_product = (
        df.groupby("ProductName", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(n)
    )
    fig = px.bar(by_product, x="Revenue", y="ProductName", orientation="h", title=f"Top {n} Products by Revenue")
    fig.update_layout(xaxis_title="Revenue", yaxis_title="Product", yaxis={"categoryorder": "total ascending"})
    return fig


def payment_method_chart(df):
    by_payment = df.groupby("PaymentMethod", as_index=False)["Revenue"].sum()
    fig = px.pie(by_payment, names="PaymentMethod", values="Revenue", title="Revenue by Payment Method")
    return fig


def loyalty_tier_chart(df):
    by_tier = df.groupby("LoyaltyTier", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
    fig = px.bar(by_tier, x="LoyaltyTier", y="Revenue", title="Revenue by Loyalty Tier")
    fig.update_layout(xaxis_title="Loyalty Tier", yaxis_title="Revenue")
    return fig


def gender_distribution_chart(df):
    unique_customers = df.drop_duplicates("CustomerID")
    by_gender = unique_customers["Gender"].value_counts().reset_index()
    by_gender.columns = ["Gender", "Count"]
    fig = px.pie(by_gender, names="Gender", values="Count", title="Customers by Gender")
    return fig


def top_customers_chart(df, n=10):
    df = df.copy()
    df["CustomerName"] = df["CustomerFirstName"] + " " + df["CustomerLastName"]
    by_customer = (
        df.groupby("CustomerName", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(n)
    )
    fig = px.bar(by_customer, x="Revenue", y="CustomerName", orientation="h", title=f"Top {n} Customers by Spend")
    fig.update_layout(xaxis_title="Revenue", yaxis_title="Customer", yaxis={"categoryorder": "total ascending"})
    return fig

def average_order_value_by_weekday(df):
    WEEKDAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df = df.copy()
    df["WeekDay"] = df["TransactionDate"].dt.day_name()
    df['WeekDay'] = pd.Categorical(df['WeekDay'], categories=WEEKDAY_ORDER, ordered=True)
    by_days = (df.groupby("WeekDay",as_index=False)["Revenue"].mean())
    fig = px.bar(by_days,x="WeekDay",y="Revenue")
    return fig