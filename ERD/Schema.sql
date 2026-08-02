CREATE TABLE Customers (
    CustomerID         VARCHAR(50) PRIMARY KEY,
    CustomerFirstName  VARCHAR(50),
    CustomerLastName   VARCHAR(50),
    Gender             VARCHAR(50),
    Phone              VARCHAR(50),
    Email              VARCHAR(50),
    LoyaltyTier        VARCHAR(50)
);

CREATE TABLE Products (
    ProductID    VARCHAR(50) PRIMARY KEY,
    ProductName  VARCHAR(50),
    Category     VARCHAR(50),
    Brand        VARCHAR(50)
);

CREATE TABLE Branches (
    BranchID    VARCHAR(50) PRIMARY KEY,
    BranchName  VARCHAR(50),
    BranchCity  VARCHAR(50)
);

CREATE TABLE Cashiers (
    CashierID    VARCHAR(50) PRIMARY KEY,
    CashierName  VARCHAR(50)
);



CREATE TABLE Transactions (
    TransactionID    VARCHAR(50) PRIMARY KEY,
    CustomerID       VARCHAR(50) REFERENCES Customers(CustomerID),
    ProductID        VARCHAR(50) REFERENCES Products(ProductID),
    BranchID         VARCHAR(50) REFERENCES Branches(BranchID),
    CashierID        VARCHAR(50) REFERENCES Cashiers(CashierID),
    Quantity         INTEGER,
    UnitPrice        NUMERIC(10, 2),
    DiscountPercent  INTEGER,
    PaymentMethod    VARCHAR(50),
    TransactionTime  TIME,
    TransactionDate  DATE
);