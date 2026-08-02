# NovaMart Retail Group — ETL Pipeline

An end-to-end ETL (Extract, Transform, Load) pipeline that takes messy, real-world-style daily sales exports from multiple retail branches, cleans and validates them, loads them into a normalized PostgreSQL database, and surfaces the results through a Streamlit dashboard.

## Overview

NovaMart operates multiple retail branches. At the end of each business day, every branch exports a single CSV file containing that day's transactions, along with the customer, product, and cashier information tied to each sale. This pipeline:

1. Picks up new CSV files as they arrive
2. Splits each file into its 5 logical entities (Transactions, Customers, Products, Branches, Cashiers)
3. Cleans and validates each entity independently
4. Cross-checks referential integrity across all 5 tables
5. Decides whether the file is clean enough to load, or needs to be rejected
6. Upserts the result into a PostgreSQL database (hosted on Neon)
7. Logs everything that happened, file by file
8. Archives the original file and moves it out of the incoming queue

A Streamlit dashboard reads from the database to visualize the results.

## Why the data is messy on purpose

This project uses synthetically generated data that deliberately includes realistic data-quality problems: missing values, inconsistent casing, mixed date formats, duplicate rows, invalid phone numbers, out-of-range discounts, and orphaned foreign key references. The point of the project is the cleaning and validation pipeline itself, not the data — a perfectly clean dataset wouldn't exercise any of it.

## Architecture

```
Branch CSV (Incoming/)
        │
        ▼
   loader.py ──────────► files.py (archives a raw copy)
        │
        ▼
  Split into 5 raw DataFrames
        │
        ▼
┌───────┴────────┬──────────┬──────────┬──────────┐
customers.py  products.py  branchs.py  cashiers.py  transactions.py
   (clean, flag quality, resolve duplicates, log issues per table)
└───────┬────────┴──────────┴──────────┴──────────┘
        │
        ▼
   finisher.py
        │
        ├── check_foreign_keys()  → cross-references every FK in
        │                            Transactions against the 4
        │                            cleaned dimension tables
        │
        ├── decide_status()       → "Processed" or "Rejected",
        │                            based on any issue tagged "Major"
        │
        ├── IF Processed:
        │     Database.py  → upserts dimensions, inserts transactions
        │                     (one all-or-nothing DB transaction)
        │     files.py     → moves file to Processed/
        │
        ├── IF Rejected:
        │     files.py     → moves file to Rejected/
        │
        └── logger.py      → appends one entry to Logs/log.json
                              either way

main.py loops this over every file currently sitting in Incoming/
```

## Project structure

```
Data/
├── Incoming/     Branch CSVs waiting to be processed
├── Raw/          Untouched archival copy of every file ever received
├── Processed/    Files that passed validation and were loaded
├── Rejected/     Files that failed validation (never touched the DB)
└── Logs/
    └── log.json  One structured entry per file ever processed

Modules/
├── config.py          Folder paths and shared constants
├── loader.py           Reads a CSV, splits it into 5 raw DataFrames
├── files.py             Copies to Raw/, moves to Processed/ or Rejected/
├── customers.py        Cleans + validates the Customers table
├── products.py         Cleans + validates the Products table
├── branchs.py           Cleans + validates the Branches table
├── cashiers.py          Cleans + validates the Cashiers table
├── transactions.py     Cleans + validates the Transactions (fact) table
├── finisher.py           Orchestrates one file end-to-end
├── Database.py          Upsert/insert logic (SQLAlchemy)
├── DBconnection.py      Database engine setup
└── logger.py             Writes to Logs/log.json

main.py                Loops over every file in Incoming/, calls finisher
schema.sql              One-time database table setup
```

## Data model

Five tables, normalized to Third Normal Form (3NF):

| Table        | Role      | Primary Key   |
| ------------ | --------- | ------------- |
| Customers    | Dimension | CustomerID    |
| Products     | Dimension | ProductID     |
| Branches     | Dimension | BranchID      |
| Cashiers     | Dimension | CashierID     |
| Transactions | Fact      | TransactionID |

`Transactions` holds foreign keys to all 4 dimension tables. Dimension tables are **upserted** (a returning customer/product/branch/cashier gets their record updated); `Transactions` is **insert-only**, since historical sales facts should never change after the fact.

See `schema.sql` for the full table definitions.

## Cleaning philosophy

Every table's cleaning module follows the same general shape:

1. **Clean formatting** — trim whitespace, standardize casing, normalize known-inconsistent values (dates, payment methods, loyalty tiers)
2. **Flag quality** — mark each row `Good` or `Bad` based on whether its important fields are present and valid, without deleting or guessing missing values
3. **Resolve duplicates** — when the same ID appears more than once, keep the `Good` version over the `Bad` one; only fall back to a `Bad` row if no `Good` version exists at all
4. **Log every issue** — every problem found gets appended to a shared list as a structured entry: `{"status": "Major" | "Minor", "table": ..., "message": ...}`

**Major vs Minor** issues determine whether a file gets rejected outright. Roughly: anything involving a broken, missing, or unresolvably conflicting identifier is Major; cosmetic or single-field problems (a malformed phone number, a missing email) are Minor.

The `Transactions` table follows a stricter rule: nothing about a transaction's own values (quantity, price, discount, date, time) ever gets auto-corrected or guessed — only flagged. A fact table's numbers shouldn't be invented.

## Referential integrity

Individual table modules only ever see their own table, so none of them can check whether a transaction's `CustomerID` actually exists in the Customers table. That check happens once, in `finisher.py`, after all 5 tables have been cleaned — it's the first point in the pipeline where all 5 DataFrames are in scope together.

## Upsert quality logic

Before overwriting an existing database row, `Database.py` compares the quality of the **incoming** row against the quality of what's **already in the database** — reusing each table's own `flag_quality()` function against the existing row, so "good" means exactly the same thing whether the data came from a fresh CSV or is already sitting in Postgres. A `Good` existing row is never silently overwritten by a `Bad` incoming one.

## Setup

1. Install dependencies:
   ```
   pip install pandas numpy sqlalchemy psycopg[binary] streamlit
   ```
2. Create a PostgreSQL database (this project uses [Neon](https://neon.tech)).
3. Run `schema.sql` against your database once, to create the 5 tables.
4. Create `Modules/DBconnection.py` with your database connection string (kept out of version control — add it to `.gitignore`):

   ```python
   import sqlalchemy

   DATABASE_CONNECTION_STRING = "your connection string here"
   engine = sqlalchemy.create_engine(DATABASE_CONNECTION_STRING)

   def get_connection():
       return engine
   ```

5. Set up the folder structure under `Data/` (`Incoming/`, `Raw/`, `Processed/`, `Rejected/`, `Logs/`).

## Running it

Drop one or more branch CSVs into `Data/Incoming/`, then run:

```
python main.py
```

Each file will be cleaned, validated, loaded (or rejected), logged, and moved out of `Incoming/`.

## Dashboard

A Streamlit dashboard reads the 5 tables from the database to visualize sales, customers, and branch performance. Data is cached with `st.cache_data` during development to avoid re-querying the database on every widget interaction.

```
streamlit run dashboard.py
```

## Known limitations / deliberate scope decisions

- Every branch is assumed to export exactly one file per day, containing only its own data. Files mixing more than one branch, or where every row has some field missing (no fully-complete row to recover from), are edge cases this project doesn't fully guard against.
- Severity (Major vs Minor) is tagged manually per issue at the point it's raised, not derived automatically.
- The dimension-vs-fact upsert strategy assumes dimension attributes (name, phone, email, etc.) are the _current_ truth and can be safely overwritten when better data arrives; no historical versioning of dimension changes is kept.
