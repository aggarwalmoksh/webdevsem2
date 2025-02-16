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
        {'name': 'BANGR FESTIVAL', 'image': 'bangrFest.jpg', 'description': 'Experience the best of Bhangra!'},
        {'name': 'ANUBHAV SINGH BASSI LIVE', 'image': 'bassiShow.jpg', 'description': 'Comedy night with Bassi!'},
        {'name': 'IPL LIVE', 'image': 'ipl.jpeg', 'description': 'Cheer for your favorite team live!'},
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
    print("Rendering index.html")
    return render_template('index.html')

# Route to get events based on selected location
@app.route('/get_events', methods=['GET'])
def get_events():
    location = request.args.get('location')
    events = events_data.get(location, [])
    print(f"Location: {location}, Events: {events}")
    return jsonify(events)


# Sign up route (now /SignUp for clarity)
@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
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

# Login route (remains /login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find the user by email
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):  # Verify password
            session['user_id'] = user.id  # Store user ID in the session
            session['username'] = user.username  # Store username in the session
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

# Route for Event Details Page
@app.route('/event/<path:event_name>')
def event_details(event_name):
    # Loop through all locations to find the event
    for location, events in events_data.items():
        for event in events:
            if event['name'] == event_name:
                return render_template('event_details.html', event=event)
    return "Event not found", 404


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    matching_events = []
    
    # Loop through all events and find matches by name
    for location, events in events_data.items():
        for event in events:
            if query in event['name'].lower():
                matching_events.append(event)
    
    return render_template('search_results.html', events=matching_events, query=query)



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
