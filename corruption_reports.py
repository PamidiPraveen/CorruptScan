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
        collection = db['corruption_reports']  # Collection for client reports

        # Fetch all documents from the collection
        data = list(collection.find({}))
        if data:
            print("Data fetched successfully from MongoDB!")
            return pd.DataFrame(data)  # Convert to DataFrame
        else:
            print("No data found in the collection!")
            return pd.DataFrame()  # Return an empty DataFrame
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return pd.DataFrame()

# Step 2: Preprocess the data
def preprocess_data(df):
    try:
        # Check if required columns exist
        required_columns = ['Fee Charged for Issue Solving (INR)', 'Amount of Corruption Taken (INR)', 'Status']
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(f"Column '{col}' not found in the data!")

        # Convert Status to binary values (1 for 'Approve', 0 for 'Reject')
        df['Status'] = df['Status'].apply(lambda x: 1 if x == 'Approve' else 0)

        # Calculate Difference
        df['Difference'] = df['Amount of Corruption Taken (INR)'] - df['Fee Charged for Issue Solving (INR)']

        # Select relevant features
        features = ['Fee Charged for Issue Solving (INR)', 'Amount of Corruption Taken (INR)', 'Difference']
        target = 'Status'

        X = df[features]  # Features
        y = df[target]    # Target variable
        return X, y
    except Exception as e:
        print(f"Error preprocessing data: {e}")
        return None, None

# Step 3: Train a machine learning model
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

# Step 4: Save the model as a .pkl file
def save_model(model, filename='corruption_model.pkl'):
    try:
        joblib.dump(model, filename)
        print(f"Model saved as {filename}")
    except Exception as e:
        print(f"Error saving the model: {e}")

# Main function
def main():
    # Step 1: Fetch data from MongoDB
    df = fetch_data_from_mongodb()
    if df.empty:
        print("No data found in MongoDB! Exiting...")
        return

    # Step 2: Preprocess the data
    X, y = preprocess_data(df)
    if X is None or y is None:
        print("Error preprocessing data! Exiting...")
        return

    # Step 3: Train the model
    model = train_model(X, y)
    if model is None:
        print("Error training the model! Exiting...")
        return

    # Step 4: Save the model
    save_model(model)

if __name__ == '__main__':
    main()