from Modules.DBconnection import get_connection
from Dashboard.components.load_data import load_data
import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns
import streamlit as st



# sales_df= load_data()
# =================
import streamlit as st
 
st.set_page_config(page_title="NovaMart Dashboard", layout="wide")
 
pages = [
    st.Page("Dashboard/pages/overview.py", title="Overview"),
    st.Page("Dashboard/pages/Sales.py", title="Sales"),
    st.Page("Dashboard/pages/Customer.py", title="Customers"),
]
 
navigation = st.navigation(pages)
navigation.run()
 
