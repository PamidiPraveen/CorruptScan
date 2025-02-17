from pymongo import MongoClient
import joblib

# Load the trained ML model
model = joblib.load('corruption_model.pkl')

# MongoDB connection
uri = "mongodb+srv://techtitanscseb:Titans1234@cluster0.um9wb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['corruptscan']
collection = db['department_details']

def fetch_fee_charged(designation):
    """Fetch Fee Charged for Issue Solving (INR) from MongoDB."""
    record = collection.find_one({'Designation': designation})
    if record:
        return record['Fee Charged for Issue Solving (INR)']
    return None

def predict_report_status(fee_charged, amount_corruption):
    """Predict whether to Approve or Reject the report."""
    difference = amount_corruption - fee_charged
    input_data = [[fee_charged, amount_corruption, difference]]
    prediction = model.predict(input_data)
    return 'Approve' if prediction[0] == 1 else 'Reject'