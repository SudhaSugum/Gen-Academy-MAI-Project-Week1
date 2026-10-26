import streamlit as st

st.set_page_config(page_title="E-commerce ROI Dashboard", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: #f3f4f6; }
    [data-testid="stSidebar"] { background: #ffffff; }
    .block-container { max-width: 1500px; padding-top: 1.5rem; padding-bottom: 3rem; }
    [data-testid="stMetric"] {
        background: #ffffff; border: 1px solid #e1e5ea; border-radius: 4px;
        padding: 1rem 1.15rem; box-shadow: 0 1px 2px rgba(17, 24, 39, .04);
    }
    [data-testid="stMetricLabel"] { color: #687386; }
    [data-testid="stMetricValue"] { color: #111827; }
    h1, h2, h3 { color: #111827; }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = [
    st.Page("pages/0_Dashboard.py", title="Dashboard", icon="📊", default=True),
    st.Page("pages/1_Overview.py", title="Overview", icon="📈"),
    st.Page("pages/2_Platform_Comparison.py", title="Channel comparison", icon="🛍️"),
    st.Page("pages/3_Campaign_Details.py", title="Campaign details", icon="📋"),
    st.Page("pages/4_Time_Series.py", title="E-commerce trends", icon="📉"),
    st.Page("pages/5_Store_Summaries.py", title="Products & Customer Segments", icon="📦"),
]
st.navigation(pages).run()
