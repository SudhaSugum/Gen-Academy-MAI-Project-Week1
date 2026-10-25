import streamlit as st

st.set_page_config(page_title="E-commerce ROI Dashboard", page_icon="📊", layout="wide")

pages = [
    st.Page("pages/0_Dashboard.py", title="Dashboard", icon="📊", default=True),
    st.Page("pages/1_Overview.py", title="Overview", icon="📈"),
    st.Page("pages/2_Platform_Comparison.py", title="Channel comparison", icon="🛍️"),
    st.Page("pages/3_Campaign_Details.py", title="Campaign details", icon="📋"),
    st.Page("pages/4_Time_Series.py", title="E-commerce trends", icon="📉"),
]
st.navigation(pages).run()
