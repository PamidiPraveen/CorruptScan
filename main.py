from pymongo import MongoClient
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

# Step 1: Connect to MongoDB and fetch data
def fetch_data_from_mongodb():
    try:
        # MongoDB Atlas connection string
        connection_string = "mongodb+srv://techtitanscseb:Titans1234@cluster0.um9wb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        # Connect to MongoDB Atlas
        client = MongoClient(connection_string)
        db = client['corruptscan']  # Database name
        
        # Fetch data from corruption_reports collection
        corruption_reports_collection = db['corruption_reports']
        corruption_data = list(corruption_reports_collection.find({}, {"_id": 0, "corruption_amount": 1, "Status": 1, "department": 1}))
        
        # Fetch data from department_details collection
        department_details_collection = db['department_details']
        department_data = list(department_details_collection.find({}, {"_id": 0, "Fee Charged for Issue Solving (INR)": 1, "department": 1}))
        
        if not corruption_data or not department_data:
            print("One or both collections are empty!")
            return None, None
        
        print("Data fetched successfully from MongoDB!")
        return pd.DataFrame(corruption_data), pd.DataFrame(department_data)
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return None, None

# Step 2: Merge data from both collections
def merge_data(corruption_df, department_df):
    try:
        # Merge data on the 'department' column
        merged_df = pd.merge(corruption_df, department_df, on='department', how='inner')
        if merged_df.empty:
            raise ValueError("No matching records found between corruption_reports and department_details!")
        return merged_df
    except Exception as e:
        print(f"Error merging data: {e}")
        return None

# Step 3: Preprocess the data
def preprocess_data(df):
    try:
        # Check if required columns exist
        REQUIRED_COLUMNS = ['Fee Charged for Issue Solving (INR)', 'corruption_amount', 'Status']
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise KeyError(f"Column '{col}' not found in the data!")
        
        # Convert Status to binary values (1 for 'Approve', 0 for 'Reject')
        df['Status'] = df['Status'].apply(lambda x: 1 if x == 'Approve' else 0)
        
        # Calculate Difference
        df['Difference'] = df['corruption_amount'] - df['Fee Charged for Issue Solving (INR)']
        
        # Select relevant features
        features = ['Fee Charged for Issue Solving (INR)', 'corruption_amount', 'Difference']
        target = 'Status'
        X = df[features]  # Features
        y = df[target]    # Target variable
        return X, y
    except Exception as e:
        print(f"Error preprocessing data: {e}")
        return None, None

# Step 4: Train a machine learning model
def train_model(X, y):
    try:
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train a Logistic Regression model
        model = LogisticRegression()
        model.fit(X_train, y_train)
        
        # Evaluate the model
        accuracy = model.score(X_test, y_test)
        print(f"Model Accuracy: {accuracy * 100:.2f}%")
        return model
    except Exception as e:
        print(f"Error training the model: {e}")
        return None

# Step 5: Save the model as a .pkl file
def save_model(model, filename='corruption_model.pkl'):
    try:
        joblib.dump(model, filename)
        print(f"Model saved as {filename}")
    except Exception as e:
        print(f"Error saving the model: {e}")

# Main function
def main():
    # Step 1: Fetch data from MongoDB
    corruption_df, department_df = fetch_data_from_mongodb()
    if corruption_df is None or department_df is None:
        print("Error fetching data! Exiting...")
        return
    
    # Step 2: Merge data from both collections
    merged_df = merge_data(corruption_df, department_df)
    if merged_df is None:
        print("Error merging data! Exiting...")
        return
    
    # Step 3: Preprocess the data
    X, y = preprocess_data(merged_df)
    if X is None or y is None:
        print("Error preprocessing data! Exiting...")
        return
    
    # Step 4: Train the model
    model = train_model(X, y)
    if model is None:
        print("Error training the model! Exiting...")
        return
    
    # Step 5: Save the model
    save_model(model)

if __name__ == '__main__':
    main()