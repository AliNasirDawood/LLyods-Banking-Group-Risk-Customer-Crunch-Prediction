# Import the load_data method from the src folder

from src.data_preprocessing import load_data

def main():
    file_path = 'data/Customer_Churn_Data_Large.xlsx'
    customer_demographics_df, transaction_history_df,customer_service_df, online_activity_df, churn_status_df = load_data(file_path)
    # Proceed with the rest of the analysis
    print("Data Loaded Successfully")

if __name__ == "__main__":
    main()
