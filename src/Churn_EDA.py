import os
import pandas as pd
import plotly.express as px
from .data_preprocessing import load_data
from src.visualisation import (
    plot_histogram,
    plot_pie,
    plot_box,
    plot_bar,
    plot_scatter,
    plot_sunburst
)

def save_visualization(fig, file_name):
    """
    Save the Plotly figure to the 'output/visuals/' folder with the specified file name.
    :param fig: Plotly figure object
    :param file_name: Name for the saved figure file
    """
    output_folder = 'output/visuals'
    os.makedirs(output_folder, exist_ok=True)  # Create the visuals folder if it doesn't exist
    fig.write_html(f'{output_folder}/{file_name}.html')  # Save as HTML file

def table_analysis(customer_demographics_df, transaction_history_df, 
                    customer_service_df, online_activity_df, churn_status_df):
    """ Perform initial table analysis and print basic info, including missing percentage. """
    # def print_missing_percent(df, name):
    #     print(f"\n{name} Missing Percentage:")
    #     missing_percent = df.isnull().mean() * 100
    #     print(missing_percent)

    # print("Customer Demographics Info:")
    # print(customer_demographics_df.info())
    # print(customer_demographics_df.columns)
    # print(customer_demographics_df.describe(include='all'))
    # print_missing_percent(customer_demographics_df, "Customer Demographics")

    # print("\nTransaction History Info:")
    # print(transaction_history_df.info())
    # print(transaction_history_df.describe(include='all'))
    # print(transaction_history_df.columns)
    # print_missing_percent(transaction_history_df, "Transaction History")

    # print("\nCustomer Service Info:")
    # print(customer_service_df.info())
    # print(customer_service_df.describe(include='all'))
    # print(customer_service_df.columns)
    # print_missing_percent(customer_service_df, "Customer Service")

    # print("\nOnline Activity Info:")
    # print(online_activity_df.info())
    # print(online_activity_df.describe(include='all'))
    # print(online_activity_df.columns)
    # print_missing_percent(online_activity_df, "Online Activity")

    # print("\nChurn Status Info:")
    # print(churn_status_df.info())
    # print(churn_status_df.describe(include='all'))
    # print(churn_status_df.columns)
    # print_missing_percent(churn_status_df, "Churn Status")


def data_visualization(customer_demographics_df, transaction_history_df, 
                       customer_service_df, online_activity_df, churn_status_df):
    """ Generate and save visualizations for each dataframe, focusing on ChurnStatus as the target. """

    # Prepare demographic features
    customer_demographics_df['AgeGroup'] = pd.cut(
        customer_demographics_df['Age'], 
        bins=[18, 30, 40, 50, 60, 100], 
        labels=['18-30', '31-40', '41-50', '51-60', '61+']
    )
    if 'Income' in customer_demographics_df.columns:
        customer_demographics_df['IncomeLevel'] = pd.qcut(
            customer_demographics_df['Income'], 4, labels=['Low', 'Medium', 'High', 'Very High']
        )

    # Merge churn status with demographics
    if 'CustomerID' in customer_demographics_df.columns and 'CustomerID' in churn_status_df.columns:
        merged_df = pd.merge(customer_demographics_df, churn_status_df, on='CustomerID', how='left')
        hierarchy_cols = ['ChurnStatus', 'AgeGroup', 'Gender', 'MaritalStatus', 'IncomeLevel']
        merged_df = merged_df.dropna(subset=hierarchy_cols)

        # Sunburst chart: ChurnStatus & Demographics
        if all(col in merged_df.columns for col in hierarchy_cols):
            fig_sunburst_churn = plot_sunburst(
                merged_df,
                path_columns=hierarchy_cols,
                title='Churn Status & Demographics Hierarchy'
            )
            save_visualization(fig_sunburst_churn, 'churn_status_demographics_sunburst')

        # Pie chart: ChurnStatus distribution
        fig_churn_pie = plot_pie(
            merged_df,
            names_column='ChurnStatus',
            title='Churn Status Distribution'
        )
        save_visualization(fig_churn_pie, 'churn_status_distribution')

        # Churn by AgeGroup
        fig_churn_age = plot_pie(
            merged_df,
            names_column='AgeGroup',
            title='Churn by Age Group',
            color_column='ChurnStatus'
        )
        save_visualization(fig_churn_age, 'churn_by_agegroup')

        # Churn by Gender
        fig_churn_gender = plot_pie(
            merged_df,
            names_column='Gender',
            title='Churn by Gender',
            color_column='ChurnStatus'
        )
        save_visualization(fig_churn_gender, 'churn_by_gender')

        # Churn by MaritalStatus
        fig_churn_marital = plot_pie(
            merged_df,
            names_column='MaritalStatus',
            title='Churn by Marital Status',
            color_column='ChurnStatus'
        )
        save_visualization(fig_churn_marital, 'churn_by_maritalstatus')

        # Churn by IncomeLevel
        fig_churn_income = plot_pie(
            merged_df,
            names_column='IncomeLevel',
            title='Churn by Income Level',
            color_column='ChurnStatus'
        )
        save_visualization(fig_churn_income, 'churn_by_incomelevel')

    # Transaction features: Total spent by churn status
    if 'CustomerID' in transaction_history_df.columns and 'AmountSpent' in transaction_history_df.columns:
        total_spent_df = transaction_history_df.groupby('CustomerID')['AmountSpent'].sum().reset_index()
        churn_spent_df = pd.merge(churn_status_df, total_spent_df, on='CustomerID', how='left')
        churn_spent_df = churn_spent_df.dropna(subset=['ChurnStatus', 'AmountSpent'])
        fig_churn_spent = plot_box(
            churn_spent_df,
            x_column='ChurnStatus',
            y_column='AmountSpent',
            title='Total Amount Spent by Churn Status'
        )
        save_visualization(fig_churn_spent, 'churn_by_total_spent')

    # Customer service: Resolution status by churn
    if 'CustomerID' in customer_service_df.columns and 'ResolutionStatus' in customer_service_df.columns:
        churn_service_df = pd.merge(churn_status_df, customer_service_df[['CustomerID', 'ResolutionStatus']], on='CustomerID', how='left')
        churn_service_df = churn_service_df.dropna(subset=['ChurnStatus', 'ResolutionStatus'])
        fig_churn_service = plot_pie(
            churn_service_df,
            names_column='ResolutionStatus',
            title='Resolution Status by Churn',
            color_column='ChurnStatus'
        )
        save_visualization(fig_churn_service, 'churn_by_resolution_status')

    # Online activity: Activity type by churn
    if 'CustomerID' in online_activity_df.columns and 'ActivityType' in online_activity_df.columns:
        churn_activity_df = pd.merge(churn_status_df, online_activity_df[['CustomerID', 'ActivityType']], on='CustomerID', how='left')
        churn_activity_df = churn_activity_df.dropna(subset=['ChurnStatus', 'ActivityType'])
        fig_churn_activity = plot_pie(
            churn_activity_df,
            names_column='ActivityType',
            title='Online Activity Type by Churn',
            color_column='ChurnStatus'
        )
        save_visualization(fig_churn_activity, 'churn_by_activity_type')

def main():
    # Step 1: Load the Data
    file_path = 'data/Customer_Churn_Data_Large.xlsx'
    customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df = load_data(file_path)
    
    # Step 2: Table Analysis (Info, Describe, Missing Percentage)
    table_analysis(customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df)

    # Step 3: Visualizations

    # --- Customer Demographics ---
    # Age distribution
    data_visualization(customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df)
    print("EDA Completed. All plots saved.")

if __name__ == "__main__":
    print("Starting EDA Process...")
    main()
