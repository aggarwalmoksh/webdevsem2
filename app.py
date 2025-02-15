from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing

# Setup the Flask application and database
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# Set up the database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize the database
db = SQLAlchemy(app)

# Sample data for events
events_data = {
    'Chandigarh': [
        {'name': 'BANGR FESTIVAL', 'image': 'bangrFest.jpg'},
        {'name': 'ANUBHAV SINGH BASSI LIVE', 'image': 'bassiShow.jpg'},
        {'name': 'IPL LIVE', 'image': 'ipl.jpeg'},
    ],
    'Shimla': []
}

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Home route
@app.route('/')
def index():
    return render_template('index.html')  # Render index.html page

# Route to get events based on selected location
@app.route('/get_events', methods=['GET'])
def get_events():
    location = request.args.get('location')  # Get location from the query parameter
    events = events_data.get(location, [])  # Fetch events for the location from the dictionary
    return jsonify(events)  # Return events as JSON response

# Sign up route
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password
        hashed_password = generate_password_hash(password)  # Hashing the password

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists, please log in.', 'danger')
            return redirect(url_for('login'))

        # Create a new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('sign_up.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find the user by email
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):  # Verify password
            session['user_id'] = user.id  # Store user ID in the session
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
