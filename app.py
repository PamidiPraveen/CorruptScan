from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import bcrypt
from datetime import datetime
import joblib  # For ML model
from data import fetch_fee_charged, predict_report_status  # Import ML and DB functions

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages and session management

# MongoDB connection
uri = "mongodb+srv://techtitanscseb:Titans1234@cluster0.um9wb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.corruptscan  # Database name
client_details = db.client_details  # Collection for client details
agent_details = db.agent_details  # Collection for agent details
corruption_reports = db.corruption_reports  # Collection for corruption reports
department_details = db.department_details  # Collection for department details

# Load the ML model
ml_model = joblib.load('corruption_model.pkl')

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for client sign-in
@app.route('/client/signin', methods=['GET', 'POST'])
def client_signin():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        # Find the client by email
        client = client_details.find_one({'email': email})

        if client:
            # Verify the password
            if bcrypt.checkpw(password.encode('utf-8'), client['password'].encode('utf-8')):
                flash('Sign in successful!', 'success')
                session['client_email'] = email  # Store client email in session
                return redirect(url_for('client_dashboard'))  # Redirect to client dashboard
            else:
                flash('Invalid email or password', 'error')
                return render_template('client_signin.html', error='Invalid email or password')
        else:
            flash('Invalid email or password', 'error')
            return render_template('client_signin.html', error='Invalid email or password')

    return render_template('client_signin.html')

# Route for client sign-up
@app.route('/client/signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        # Get form data
        client_data = {
            'name': request.form.get('name'),
            'mobile': request.form.get('mobile'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'state': request.form.get('state'),
            'district': request.form.get('district'),
            'age': int(request.form.get('age')),
            'profession': request.form.get('profession'),
            'aadhaar': request.form.get('aadhaar'),
            'gender': request.form.get('gender'),
            'password': bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Hash password
        }

        # Check if the email already exists in the database
        existing_client = client_details.find_one({'email': client_data['email']})
        if existing_client:
            flash('Email already exists!', 'error')
            return render_template('client_signup.html', error='Email already exists!')

        # Insert new client into the database
        client_details.insert_one(client_data)
        flash('Sign up successful! Please sign in.', 'success')
        return redirect(url_for('client_signin'))

    return render_template('client_signup.html')

# Route for agent sign-in
@app.route('/agent/signin', methods=['GET', 'POST'])
def agent_signin():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        # Find the agent by email
        agent = agent_details.find_one({'email': email})

        if agent:
            # Verify the password
            if bcrypt.checkpw(password.encode('utf-8'), agent['password'].encode('utf-8')):
                flash('Sign in successful!', 'success')
                session['agent_email'] = email  # Store agent email in session
                return redirect(url_for('agent_dashboard'))  # Redirect to agent dashboard
            else:
                flash('Invalid email or password', 'error')
                return render_template('agent_signin.html', error='Invalid email or password')
        else:
            flash('Invalid email or password', 'error')
            return render_template('agent_signin.html', error='Invalid email or password')

    return render_template('agent_signin.html')

# Route for agent sign-up
@app.route('/agent/signup', methods=['GET', 'POST'])
def agent_signup():
    if request.method == 'POST':
        # Get form data
        agent_data = {
            'name': request.form.get('name'),
            'mobile': request.form.get('mobile'),
            'email': request.form.get('email'),
            'department': request.form.get('department'),
            'designation': request.form.get('designation'),
            'password': bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Hash password
        }

        # Check if the email already exists in the database
        existing_agent = agent_details.find_one({'email': agent_data['email']})
        if existing_agent:
            flash('Email already exists!', 'error')
            return render_template('agent_signup.html', error='Email already exists!')

        # Insert new agent into the database
        agent_details.insert_one(agent_data)
        flash('Sign up successful! Please sign in.', 'success')
        return redirect(url_for('agent_signin'))

    return render_template('agent_signup.html')

# Route for reporting corruption
@app.route('/report/corruption', methods=['GET', 'POST'])
def report_corruption():
    if 'client_email' not in session:
        flash('Please sign in to report corruption.', 'error')
        return redirect(url_for('client_signin'))

    if request.method == 'POST':
        try:
            # Fetch department details
            department_data = department_details.find_one({'Department Name': request.form.get('department')})
            if not department_data:
                flash('Invalid department!', 'error')
                return redirect(url_for('report_corruption'))

            amount = department_data["Fee Charged for Issue Solving (INR)"]
            corruption_amount = float(request.form.get('corruption_amount'))

            # Determine status
            status = 'approved' if corruption_amount >= amount else 'rejected'

            # Prepare report data
            report_data = {
                'client_email': session['client_email'],
                'department': request.form.get('department'),
                'designation': request.form.get('designation'),
                'employee_name': request.form.get('employee_name'),
                'complaint_desc': request.form.get('complaint_desc'),
                'complainee_name': request.form.get('complainee_name'),
                'corruption_amount': corruption_amount,
                'eyewitness_name': request.form.get('eyewitness_name'),
                'eyewitness_address': request.form.get('eyewitness_address'),
                'eyewitness_age': request.form.get('eyewitness_age'),
                'proofs': request.files['proofs'].read(),  # Store file as binary data
                'status': status,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Insert report into the database
            corruption_reports.insert_one(report_data)
            flash('Report submitted successfully!', 'success')
            return redirect(url_for('client_dashboard'))

        except Exception as e:
            print("Error submitting report:", str(e))
            flash('An error occurred while submitting the report. Please try again.', 'error')
            return redirect(url_for('report_corruption'))

    return render_template('report_corruption.html')

# Route for client dashboard
@app.route('/client/dashboard', methods=['GET'])
def client_dashboard():
    if 'client_email' not in session:
        flash('Please sign in to access the dashboard.', 'error')
        return redirect(url_for('client_signin'))

    # Fetch all reports for the logged-in client
    client_email = session['client_email']
    reports = list(corruption_reports.find({'client_email': client_email}))

    return render_template('client_dashboard.html', reports=reports)

# Route for agent dashboard
@app.route('/agent/dashboard', methods=['post','get'])
def agent_dashboard():
    if 'agent_email' not in session:
        flash('Please sign in to access the dashboard.', 'error')
        return redirect(url_for('agent_signin'))

    # Fetch agent details
    agent_email = session['agent_email']
    agent = agent_details.find_one({'email': agent_email})

    if not agent:
        flash('Agent not found.', 'error')
        return redirect(url_for('agent_signin'))

    # Stats (Total and Pending Reports)
    total_reports = corruption_reports.count_documents({})
    pending_reports = corruption_reports.count_documents({'status': 'pending'})

    # Form handling: GET request (for filtering reports)
    if request.method == 'GET':
        # If an agent submits the form to filter reports
        status_filter = request.args.get('status', default='approved', type=str)
        reports = list(corruption_reports.find({"status": status_filter}))
    else:
        # If an agent submits a form to update report status (POST request)
        report_id = request.form.get('report_id')
        new_status = request.form.get('status')
        if report_id and new_status:
            corruption_reports.update_one({'_id': report_id}, {'$set': {'status': new_status}})
            flash('Report status updated!', 'success')
            return redirect(url_for('agent_dashboard'))

    return render_template('agent_dashboard.html', agent=agent, total_reports=total_reports,
                           pending_reports=pending_reports, reports=reports)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=1234,
        debug=True
    )