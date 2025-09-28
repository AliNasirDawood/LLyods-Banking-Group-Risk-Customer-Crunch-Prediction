import pandas as pd

def load_data(file_path):
    """
    Load the Excel file and return dataframes for each sheet.
    """
    xls = pd.ExcelFile(file_path)
    
    # Load data for each sheet into separate dataframes
    customer_demographics_df = pd.read_excel(xls, sheet_name='Customer_Demographics')
    transaction_history_df = pd.read_excel(xls, sheet_name='Transaction_History')
    customer_service_df = pd.read_excel(xls, sheet_name='Customer_Service')
    online_activity_df = pd.read_excel(xls, sheet_name='Online_Activity')
    churn_status_df = pd.read_excel(xls, sheet_name='Churn_Status')

    # Return all dataframes
    return customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df

def feature_extraction(customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df):
    """
    Perform feature extraction: combine datasets and create new features.
    """
    
    # Combine datasets based on CustomerID
    df = pd.merge(customer_demographics_df, churn_status_df, on='CustomerID', how='left')
    df = pd.merge(df, transaction_history_df, on='CustomerID', how='left')
    df = pd.merge(df, customer_service_df, on='CustomerID', how='left')
    df = pd.merge(df, online_activity_df, on='CustomerID', how='left')
    
   # Drop Date Time Columns
    
    # Feature: Total spending (aggregation)
    df['TotalSpent'] = df.groupby('CustomerID')['AmountSpent'].transform('sum')
      
    # Feature: Login Frequency (aggregated)
    df['LoginFrequency'] = df.groupby('CustomerID')['LoginFrequency'].transform('count')

    # Product category frequency 
    
    
    return df


    

from sklearn.impute import IterativeImputer

def handling_missing_data(df):
    """
    Handle missing data by creating missing indicators and using MICE imputation.
    """
    # Missing Indicator: Create a binary indicator for missing values in each column
    missing_indicators = df.isnull().astype(int)
    
    # Impute missing values using MICE (Multiple Imputation by Chained Equations)
    imputer = IterativeImputer(random_state=42)
    df_imputed = df.copy()
    df_imputed = pd.DataFrame(imputer.fit_transform(df_imputed), columns=df_imputed.columns)
    
    # Combine missing indicators with imputed data (optional)
    df_imputed = df_imputed.join(missing_indicators, rsuffix='_missing')
    
    return df_imputed
# Load data from the Excel file
file_path = 'path_to_your_excel_file.xlsx'
customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df = load_data(file_path)

# Feature extraction: Combine datasets and create new features
df = feature_extraction(customer_demographics_df, transaction_history_df, customer_service_df, online_activity_df, churn_status_df)

# Handle missing data: Apply missing indicator and impute missing values
df_imputed = handling_missing_data(df)

# Display the imputed dataframe
print(df_imputed.head())








