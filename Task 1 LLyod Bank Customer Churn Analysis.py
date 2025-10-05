
from io import BytesIO
from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide", page_title="Lloyds Customer Churn Dashboard")

col1, col2 = st.columns([1, 6])
with col1:
    st.image("assets/logo.jpeg", width=500)
with col2:
    st.markdown(
        "<h1 style='color:white; margin-top:20px;'>Lloyds Banking Group - Customer Churn Dashboard</h1>",
        unsafe_allow_html=True,
    )

st.caption(
    "This report outlines exploratory data analysis (EDA) performed on a customer churn dataset. The goal is to understand customer behavior and identify key factors contributing to churn."
)

DATA_PATH = Path(__file__).resolve().parent / "data" / "Customer_Churn_Data_Large.xlsx"
SHEETS = [
    "Customer_Demographics",
    "Transaction_History",
    "Customer_Service",
    "Online_Activity",
    "Churn_Status",
]
DATE_COLUMNS = {
    "Transaction_History": ["TransactionDate"],
    "Customer_Service": ["InteractionDate"],
    "Online_Activity": ["LastLoginDate"],
}
STATUS_LABELS = {0: "Active", 1: "Churned"}
STATUS_COLORS = {"Active": "#024A02", "Churned": "#4ad627", "Unknown": "#cdf9d6"}
STATUS_LABELS_GENDER = {"M": "Male", "F": "Female"}

THEME_COLOR_SEQUENCE = [
    "#024A02",
    "#4ad627",
    "#cdf9d6",
    "#0b2e13",
    "#6bce58",
    "#aee9b7",
]
px.defaults.color_discrete_sequence = THEME_COLOR_SEQUENCE

@st.cache_data(show_spinner="Loading workbook...")
def load_workbook(source):
    if isinstance(source, (str, Path)):
        file_obj = source
    else:
        file_obj = BytesIO(source)
    xls = pd.ExcelFile(file_obj)
    sheet_set = set(xls.sheet_names)
    missing = [sheet for sheet in SHEETS if sheet not in sheet_set]
    if missing:
        raise ValueError(f"Workbook is missing sheets: {', '.join(missing)}")
    frames = {sheet: xls.parse(sheet) for sheet in SHEETS}
    for sheet, cols in DATE_COLUMNS.items():
        frame = frames.get(sheet)
        for col in cols:
            if col in frame.columns:
                frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frames


def format_currency(value):
    if pd.isna(value):
        return "-"
    return f"GBP {value:,.0f}"


st.title("Lloyds Banking Group - Customer Churn Dashboard")
st.caption(
    "This report outlines the data gathering and exploratory data analysis (EDA) performed on a customer churn dataset. The goal is to understand customer behavior and identify key features that contribute to customer churn."
)

with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Upload Excel workbook", type="xlsx")
    st.caption("Leave blank to use the bundled sample workbook.")
    if uploaded_file:
        data_source = uploaded_file.getvalue()
    else:
        if not DATA_PATH.exists():
            st.error("Upload a workbook or place Customer_Churn_Data_Large.xlsx in the data folder.")
            st.stop()
        data_source = str(DATA_PATH)
    try:
        data = load_workbook(data_source)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

customer_demographics = data["Customer_Demographics"]
customer_service = data["Customer_Service"]
online_activity = data["Online_Activity"]
transaction_history = data["Transaction_History"]
churn_status = data["Churn_Status"]

customer_base = customer_demographics.merge(churn_status, on="CustomerID", how="left")
customer_base = customer_base.merge(online_activity, on="CustomerID", how="left")
customer_base["ChurnLabel"] = customer_base["ChurnStatus"].map(STATUS_LABELS).fillna("Unknown")

with st.sidebar:
    st.subheader("Filters")
    age_min = int(customer_base["Age"].min())
    age_max = int(customer_base["Age"].max())
    age_range = st.slider("Age range", age_min, age_max, (age_min, age_max))
    gender_options = sorted(customer_base["Gender"].dropna().unique().tolist())
    selected_gender = (
        st.multiselect("Gender", gender_options, default=gender_options) if gender_options else []
    )
    income_options = sorted(customer_base["IncomeLevel"].dropna().unique().tolist())
    selected_income = (
        st.multiselect("Income level", income_options, default=income_options)
        if income_options
        else []
    )
    marital_options = sorted(customer_base["MaritalStatus"].dropna().unique().tolist())
    selected_marital = (
        st.multiselect("Marital status", marital_options, default=marital_options)
        if marital_options
        else []
    )
    status_options = [STATUS_LABELS[key] for key in sorted(STATUS_LABELS)]
    selected_status = st.multiselect("Churn status", status_options, default=status_options)

filtered_customers = customer_base[customer_base["Age"].between(age_range[0], age_range[1])]
if selected_gender:
    filtered_customers = filtered_customers[filtered_customers["Gender"].isin(selected_gender)]
if selected_income:
    filtered_customers = filtered_customers[filtered_customers["IncomeLevel"].isin(selected_income)]
if selected_marital:
    filtered_customers = filtered_customers[
        filtered_customers["MaritalStatus"].isin(selected_marital)
    ]
if selected_status:
    status_values = [code for code, label in STATUS_LABELS.items() if label in selected_status]
    filtered_customers = filtered_customers[
        filtered_customers["ChurnStatus"].isin(status_values)
    ]

filtered_customers = filtered_customers.copy()
if filtered_customers.empty:
    st.warning("No customers match the current filters. Adjust the filters to continue.")
    st.stop()

filtered_customer_ids = filtered_customers["CustomerID"].tolist()

transactions_filtered = transaction_history[
    transaction_history["CustomerID"].isin(filtered_customer_ids)
].copy()
if not transactions_filtered.empty:
    transactions_filtered = transactions_filtered.merge(
        filtered_customers[["CustomerID", "ChurnStatus", "ChurnLabel"]],
        on="CustomerID",
        how="left",
    )
    transactions_filtered["TransactionMonth"] = transactions_filtered["TransactionDate"].dt.to_period(
        "M"
    ).dt.to_timestamp()
else:
    transactions_filtered["ChurnStatus"] = pd.Series(dtype=float)
    transactions_filtered["ChurnLabel"] = pd.Series(dtype=object)
    transactions_filtered["TransactionMonth"] = pd.Series(dtype="datetime64[ns]")

service_filtered = customer_service[
    customer_service["CustomerID"].isin(filtered_customer_ids)
].copy()
if not service_filtered.empty:
    service_filtered = service_filtered.merge(
        filtered_customers[["CustomerID", "ChurnLabel"]], on="CustomerID", how="left"
    )
else:
    service_filtered["ChurnLabel"] = pd.Series(dtype=object)

online_filtered = filtered_customers[
    ["CustomerID", "LoginFrequency", "ServiceUsage", "LastLoginDate", "ChurnLabel"]
].copy()

total_customers = filtered_customers["CustomerID"].nunique()
churn_rate = filtered_customers["ChurnStatus"].mean()
total_spend = transactions_filtered["AmountSpent"].sum() if not transactions_filtered.empty else float("nan")
total_categories = transactions_filtered["ProductCategory"].nunique() if not transactions_filtered.empty else 0

overview_tab,explore_tab = st.tabs(
    ["Data Analysis", "Data Explorer"]
)

with overview_tab:
    kpi_columns = st.columns(4)
    with kpi_columns[0]:
        st.metric("Customers", f"{total_customers:,}")
    with kpi_columns[1]:
        churn_metric = "-" if pd.isna(churn_rate) else f"{churn_rate * 100:.1f}%"
        st.metric("Churn rate", churn_metric)
    with kpi_columns[2]:
        st.metric("Total transaction amount", format_currency(total_spend))
    with kpi_columns[3]:
        st.metric("Total Amount of Categories", f"{total_categories:,}")

    ## Demographics charts
    st.subheader("Customer Demographics")

    demo_columns = st.columns(4)
    with demo_columns[2]:
        if filtered_customers["Gender"].dropna().empty:
            st.info("Gender data unavailable for the current selection.")
        else:
            gender_chart = px.pie(
                filtered_customers,
                names="Gender",
                title="Gender mix",
                color="Gender",
                color_discrete_sequence=THEME_COLOR_SEQUENCE,
            )
            st.plotly_chart(gender_chart, use_container_width=True)
    with demo_columns[0]:
        income_counts = (
            filtered_customers.dropna(subset=["IncomeLevel"])
            .groupby(["IncomeLevel", "ChurnLabel"])
            .size()
            .reset_index(name="Count")
        )
        if income_counts.empty:
            st.info("Income level data unavailable for the current selection.")
        else:
            income_chart = px.bar(
                income_counts,
                x="IncomeLevel",
                y="Count",
                color="ChurnLabel",
                barmode="overlay",
                color_discrete_map=STATUS_COLORS,
                labels={"IncomeLevel": "Income level", "Count": "Customers"},
                title="Income level vs churn status",
            )
            income_chart.update_layout(legend_title=None)
            st.plotly_chart(income_chart, use_container_width=True)
    with demo_columns[1]:

        age_chart = px.histogram(
            filtered_customers,
            x="Age",
            color="ChurnLabel",
            nbins=15,
            barmode="overlay",
            color_discrete_map=STATUS_COLORS,
            labels={"Age": "Age", "count": "Customers"},
            title="Age distribution",
    )
        age_chart.update_layout(legend_title=None)
        st.plotly_chart(age_chart, use_container_width=True)
    with demo_columns[3]:

        churn_by_marital = (
            filtered_customers.dropna(subset=["MaritalStatus"])
            .groupby("MaritalStatus", as_index=False)["ChurnStatus"]
            .mean()
        )
        churn_by_marital["ChurnRatePct"] = churn_by_marital["ChurnStatus"] * 100
        if churn_by_marital.empty:
            st.info("Marital status data unavailable for the current selection.")
        else:
            marital_chart = px.bar(
                churn_by_marital,
                x="MaritalStatus",
                y="ChurnRatePct",
                labels={"MaritalStatus": "Marital status", "ChurnRatePct": "Churn rate (%)"},
                title="Churn rate by marital status",
            )
            marital_chart.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            marital_chart.update_yaxes(ticksuffix="%")
            st.plotly_chart(marital_chart, use_container_width=True)
    
    # Transaction Charts
    st.subheader("Product categories (churned customers)")
    demo_columns = st.columns(3)
    with demo_columns[0]:
        
        if "ChurnStatus" in transactions_filtered.columns:
            churned_transactions = transactions_filtered[
                transactions_filtered["ChurnStatus"] == 1
            ]
        else:
            churned_transactions = pd.DataFrame(columns=transactions_filtered.columns)
        if churned_transactions.empty:
            st.info("No churned transactions for the current selection.")
        else:
            product_counts = (
                churned_transactions["ProductCategory"].value_counts().reset_index()
            )
            product_counts.columns = ["ProductCategory", "Count"]
            product_chart = px.bar(
                product_counts,
                x="ProductCategory",
                y="Count",
                labels={"ProductCategory": "Product category", "Count": "Transactions"},
                title="Top product categories among churned customers",
            )
            st.plotly_chart(product_chart, use_container_width=True)
    with demo_columns[1]:

        if transactions_filtered.empty:
            st.info("No transactions for the current selection.")
        else:
            spend_chart = px.histogram(
                transactions_filtered,
                x="AmountSpent",
                color="ChurnLabel",
                nbins=30,
                barmode="overlay",
                color_discrete_map=STATUS_COLORS,
                labels={"AmountSpent": "Amount spent", "count": "Transactions"},
                title="Transaction amount distribution",
            )
            spend_chart.update_layout(legend_title=None)
            st.plotly_chart(spend_chart, use_container_width=True)
    with demo_columns[2]:
        avg_ticket = (
            transactions_filtered.groupby("ChurnLabel", as_index=False)["AmountSpent"]
            .mean()
        )
        avg_ticket["AmountLabel"] = avg_ticket["AmountSpent"].apply(format_currency)
        avg_chart = px.bar(
            avg_ticket,
            x="ChurnLabel",
            y="AmountSpent",
            color="ChurnLabel",
            color_discrete_map=STATUS_COLORS,
            text="AmountLabel",
            labels={"ChurnLabel": "Churn status", "AmountSpent": "Average amount (GBP)"},
            title="Average transaction amount by churn status",
        )
        avg_chart.update_traces(textposition="outside", showlegend=False)
        avg_chart.update_yaxes(tickprefix="GBP ", tickformat=",")
        st.plotly_chart(avg_chart, use_container_width=True)
    
    
    st.subheader("Digital engagement")
    
    service_columns = st.columns(4)
    with service_columns[0]:
        if service_filtered.empty:
            st.info("No service interactions for the current selection.")
        else:
            resolution_chart = px.histogram(
                service_filtered,
                x="ResolutionStatus",
                color="ChurnLabel",
                barmode="group",
                color_discrete_map=STATUS_COLORS,
                labels={"ResolutionStatus": "Resolution status", "count": "Interactions"},
                title="Resolution outcomes by churn status",
            )
            resolution_chart.update_layout(legend_title=None)
            st.plotly_chart(resolution_chart, use_container_width=True)
    with service_columns[1]:
        if service_filtered.empty:
            st.empty()
        else:
            interaction_chart = px.pie(
                service_filtered,
                names="InteractionType",
                title="Interaction types",
                color_discrete_sequence=THEME_COLOR_SEQUENCE,
            )
            st.plotly_chart(interaction_chart, use_container_width=True)
    with service_columns[2]:
        
        usage_counts = (
            online_filtered.dropna(subset=["ServiceUsage"])
            .groupby(["ServiceUsage", "ChurnLabel"])
            .size()
            .reset_index(name="Count")
        )
        if usage_counts.empty:
            st.info("Service usage data unavailable for the current selection.")
        else:
            usage_chart = px.bar(
                usage_counts,
                x="ServiceUsage",
                y="Count",
                color="ChurnLabel",
                barmode="stack",
                color_discrete_map=STATUS_COLORS,
                labels={"ServiceUsage": "Service usage", "Count": "Customers"},
                title="Preferred digital services",
            )
            usage_chart.update_layout(legend_title=None)
            st.plotly_chart(usage_chart, use_container_width=True)
    with service_columns[3]:


        login_data = online_filtered.dropna(subset=["LoginFrequency"])
        if login_data.empty:
            st.info("Login frequency data unavailable for the current selection.")
        else:
            login_chart = px.histogram(
                login_data,
                x="LoginFrequency",
                color="ChurnLabel",
                nbins=15,
                barmode="overlay",
                color_discrete_map=STATUS_COLORS,
                labels={"LoginFrequency": "Logins per month", "count": "Customers"},
                title="Login frequency distribution",
            )
            login_chart.update_layout(legend_title=None)
            st.plotly_chart(login_chart, use_container_width=True)

            
with explore_tab:
    st.subheader("Data Explorer")
    tables = {
        "Customers (filtered)": filtered_customers.sort_values("CustomerID"),
        "Transactions (filtered)": transactions_filtered.sort_values("TransactionDate")
        if "TransactionDate" in transactions_filtered.columns
        else transactions_filtered,
        "Customer Service (filtered)": service_filtered.sort_values("InteractionDate")
        if "InteractionDate" in service_filtered.columns
        else service_filtered,
        "Online Activity (filtered)": online_filtered.sort_values("LastLoginDate"),
        "Churn Status (full)": churn_status.sort_values("CustomerID"),
    }
    table_name = st.selectbox("Select a table", list(tables.keys()))
    table_df = tables[table_name]
    st.dataframe(table_df, use_container_width=True)
    csv_data = table_df.to_csv(index=False).encode("utf-8")
    safe_name = "".join(ch for ch in table_name if ch.isalnum() or ch in (" ", "_")).strip()
    download_name = f"{safe_name.replace(' ', '_').lower()}.csv"
    st.download_button("Download CSV", data=csv_data, file_name=download_name, mime="text/csv")

# import plotly.graph_objects as go


# Assuming you have filtered customer data in filtered_customers
# Merge filtered_customers with transaction_history to include ProductCategory
# merged_data = filtered_customers.merge(transaction_history[['CustomerID', 'ProductCategory']], on='CustomerID', how='left')

# # Aggregate the data: count customers for each combination of the categories
# flow_data = merged_data.groupby(['IncomeLevel', 'ProductCategory', 'ServiceUsage', 'ChurnLabel']).size().reset_index(name='Count')

# # Define the labels (nodes) from all categories: IncomeLevel, ProductCategory, ServiceUsage, ChurnLabel
# labels = list(flow_data['IncomeLevel'].unique()) + \
#          list(flow_data['ProductCategory'].unique()) + \
#          list(flow_data['ServiceUsage'].unique()) + \
#          list(flow_data['ChurnLabel'].unique())

# # Create a mapping from category values to node indices
# label_dict = {label: i for i, label in enumerate(labels)}

# # Define the sources and targets based on the flow from one category to another
# # For example, IncomeLevel -> ProductCategory, ProductCategory -> ServiceUsage, ServiceUsage -> ChurnStatus
# sources = []
# targets = []
# values = []

# # Map the flows between IncomeLevel -> ProductCategory
# for _, row in flow_data.iterrows():
#     source_idx = label_dict[row['IncomeLevel']]
#     target_idx = label_dict[row['ProductCategory']]
#     sources.append(source_idx)
#     targets.append(target_idx)
#     values.append(row['Count'])

# # Map the flows between ProductCategory -> ServiceUsage
# for _, row in flow_data.iterrows():
#     source_idx = label_dict[row['ProductCategory']]
#     target_idx = label_dict[row['ServiceUsage']]
#     sources.append(source_idx)
#     targets.append(target_idx)
#     values.append(row['Count'])

# # Map the flows between ServiceUsage -> ChurnLabel
# for _, row in flow_data.iterrows():
#     source_idx = label_dict[row['ServiceUsage']]
#     target_idx = label_dict[row['ChurnLabel']]
#     sources.append(source_idx)
#     targets.append(target_idx)
#     values.append(row['Count'])

# # Create the Sankey diagram
# fig = go.Figure(go.Sankey(
#     node=dict(
#         pad=15,
#         thickness=20,
#         label=labels,
#         color="#024A02"  # Consistent color for nodes
#     ),
#     link=dict(
#         source=sources,
#         target=targets,
#         value=values,
#         color="#8cfc70"  # Consistent color for links
#     )
# ))

# # Customize the layout
# fig.update_layout(
#     title="Flow from Income Level â†’ Product Category â†’ Service Usage â†’ Churn Status",
#     font_size=11,
#     height=650
# )

# # Display the Sankey diagram in Streamlit
# st.plotly_chart(fig, use_container_width=True)


st.caption("Churn status: 1 = churned, 0 = active.")
