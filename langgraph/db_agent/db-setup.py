import pandas as pd
import sqlite3

df = pd.read_csv("telco.csv")

df.columns = df.columns.str.replace(' ', '_')

customer_df = df[['Customer_ID', 'Gender', 'Age', 'Under_30', 'Senior_Citizen', 'Married', 'Dependents', 'Number_of_Dependents', 'Country', 'State', 'City', 'Zip_Code', 'Latitude', 'Longitude', 'Population']]
service_df = df[['Customer_ID', 'Phone_Service', 'Multiple_Lines', 'Internet_Service', 'Internet_Type', 'Online_Security', 'Online_Backup', 'Device_Protection_Plan', 'Premium_Tech_Support', 'Streaming_TV', 'Streaming_Movies', 'Streaming_Music', 'Unlimited_Data']]
billing_df = df[['Customer_ID', 'Tenure_in_Months', 'Offer', 'Avg_Monthly_Long_Distance_Charges', 'Avg_Monthly_GB_Download', 'Contract', 'Paperless_Billing', 'Payment_Method', 'Monthly_Charge', 'Total_Charges', 'Total_Refunds', 'Total_Extra_Data_Charges', 'Total_Long_Distance_Charges', 'Total_Revenue']]
referral_df = df[['Customer_ID', 'Referred_a_Friend', 'Number_of_Referrals']]
churn_df = df[['Customer_ID', 'Quarter', 'Satisfaction_Score', 'Customer_Status', 'Churn_Label', 'Churn_Score', 'CLTV', 'Churn_Category', 'Churn_Reason']]

conn = sqlite3.connect('telco.db')

customer_df.to_sql('Customer', conn, if_exists='replace', index=False)
service_df.to_sql('Service', conn, if_exists='replace', index=False)
billing_df.to_sql('Billing', conn, if_exists='replace', index=False)
referral_df.to_sql('Referral', conn, if_exists='replace', index=False)
churn_df.to_sql('Churn', conn, if_exists='replace', index=False)

conn.close()