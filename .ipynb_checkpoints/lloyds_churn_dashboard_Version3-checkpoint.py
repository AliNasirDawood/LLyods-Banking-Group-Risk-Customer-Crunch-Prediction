import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

st.set_page_config(layout="wide", page_title="Lloyds Customer Churn Dashboard")

st.title("Lloyds Banking Group - Customer Churn Dashboard")

# --- Data Upload ---
st.sidebar.header("1. Data Upload")
xls_file = st.sidebar.file_uploader("Upload Customer_Churn_Data_Large.xlsx", type=["xlsx"])
if xls_file:
    # Read relevant sheets
    st.sidebar.success("File uploaded, loading sheets...")
    demo = pd.read_excel(xls_file, sheet_name="Customer_Demographics")
    tx = pd.read_excel(xls_file, sheet_name="Transaction_History")
    service = pd.read_excel(xls_file, sheet_name="Customer_Service")
    online = pd.read_excel(xls_file, sheet_name="Online_Activity")
    churn = pd.read_excel(xls_file, sheet_name="Churn_Status")

    # --- Data Preview ---
    st.header("Data Preview")
    st.write("Customer Demographics", demo.head())
    st.write("Transaction History", tx.head())
    st.write("Customer Service", service.head())
    st.write("Online Activity", online.head())
    st.write("Churn Status", churn.head())

    # --- Merge For Analysis ---
    df = demo.merge(churn, on="CustomerID", how="left")
    tx_full = tx.merge(churn, on="CustomerID", how="left")
    online_full = online.merge(churn, on="CustomerID", how="left")
    service_full = service.merge(churn, on="CustomerID", how="left")

    # --- Churn Overview ---
    st.header("Churn Overview")
    churn_rate = df["ChurnStatus"].mean()
    st.metric("Churn Rate", f"{100*churn_rate:.1f}%")
    fig = px.pie(df, names="ChurnStatus", title="Churn Distribution", color="ChurnStatus",
                 color_discrete_map={0: "green", 1: "red"}, labels={"ChurnStatus": {0: "Not Churned", 1: "Churned"}})
    st.plotly_chart(fig, use_container_width=True)

    # --- Churn Over Time ---
    if "TransactionDate" in tx_full.columns:
        st.header("Churn Over Time")
        tx_full["Month"] = pd.to_datetime(tx_full["TransactionDate"]).dt.to_period("M")
        churn_time = tx_full.groupby(["Month", "ChurnStatus"]).size().unstack().fillna(0)
        churn_time = churn_time.rename(columns={0: "Not Churned", 1: "Churned"})
        fig = px.line(churn_time, y=["Churned", "Not Churned"], labels={"value": "Transactions", "Month": "Month"})
        st.plotly_chart(fig, use_container_width=True)

    # --- Demographics Breakdown ---
    st.header("Demographics Breakdown (Churned Only)")
    churned = df[df["ChurnStatus"] == 1]
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.histogram(churned, x="Age", nbins=15, title="Age")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(churned, names="Gender", title="Gender")
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = px.pie(churned, names="IncomeLevel", title="Income Level")
        st.plotly_chart(fig, use_container_width=True)

    # --- Segment Analysis (KMeans) ---
    st.header("Customer Segmentation (KMeans Clustering)")
    seg_features = ["Age"]
    if "IncomeLevel" in churned and churned["IncomeLevel"].nunique() > 1:
        income_map = {k: i for i, k in enumerate(churned["IncomeLevel"].unique())}
        seg_features.append("IncomeLevel")
        churned["IncomeLevelNum"] = churned["IncomeLevel"].map(income_map)
    else:
        churned["IncomeLevelNum"] = 0

    X_seg = churned[["Age", "IncomeLevelNum"]].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_seg)
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X_scaled)
    churned["Cluster"] = kmeans.labels_
    fig = px.scatter(churned, x="Age", y="IncomeLevelNum", color="Cluster",
                     title="Customer Segments (Churned)", labels={"IncomeLevelNum": "Income Level"})
    st.plotly_chart(fig, use_container_width=True)

    # --- Service Impact ---
    st.header("Customer Service Impact on Churn")
    if not service_full.empty:
        fig = px.histogram(service_full, x="ResolutionStatus", color="ChurnStatus",
                           barmode="group", title="Resolution Status by Churn", 
                           labels={"ChurnStatus": "Churned"})
        st.plotly_chart(fig, use_container_width=True)

    # --- Predictive Modeling ---
    st.header("Churn Prediction & Feature Importance")
    # Prepare model data using demo + online + churn
    model_df = demo.merge(online, on="CustomerID", how="left").merge(churn, on="CustomerID")
    y = model_df["ChurnStatus"]
    feature_cols = ["Age", "Gender", "IncomeLevel", "LoginFrequency", "DaysSinceLastLogin", "ServiceUsage"]
    X = model_df[feature_cols].copy()

    # Encode categoricals
    for col in ["Gender", "IncomeLevel", "ServiceUsage"]:
        if col in X: X[col] = LabelEncoder().fit_transform(X[col].astype(str))
    X = X.fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    importances = pd.Series(clf.feature_importances_, index=X.columns).sort_values(ascending=False)
    st.write("Test Accuracy:", clf.score(X_test, y_test))
    fig = px.bar(importances, orientation="h", title="Feature Importances")
    st.plotly_chart(fig, use_container_width=True)

    # --- Interactive Exploration ---
    st.header("Interactive Data Exploration")
    table_opts = {
        "Customer Demographics": demo,
        "Transaction History": tx,
        "Customer Service": service,
        "Online Activity": online,
        "Churn Status": churn
    }
    tbl = st.selectbox("Choose a data table to explore", list(table_opts.keys()))
    st.dataframe(table_opts[tbl].sample(10))

    st.sidebar.info("Dashboard includes: Churn trends, segmentation, service impact, and modeling. Expand as needed!")

else:
    st.info("Please upload the Excel file in the sidebar to begin.")