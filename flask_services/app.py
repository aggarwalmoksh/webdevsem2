from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Data for About Us page
about_data = {
    "title": "About District Events",
    "description": "Your premier destination for discovering and booking exclusive events in your city.",
    "content": """
        <h3 class="mb-4">Our Story</h3>
        <p>District Events was born from a passion for connecting people with extraordinary experiences. Founded in 2023, we set out to create a platform that makes discovering and booking premium events effortless.</p>

        <p>Our platform curates high-quality experiences from concerts and theater performances to workshops and exhibitions, ensuring that you have access to the best events in your city.</p>

        <h3 class="mt-5 mb-4">Our Mission</h3>
        <p>Our mission is to enrich lives through exceptional events while supporting event organizers and venues in showcasing their best offerings. We believe that memorable experiences create lasting connections and foster community engagement.</p>

        <h3 class="mt-5 mb-4">Why Choose District Events?</h3>
        <ul>
            <li>Curated Selection: We handpick the finest events to ensure quality experiences.</li>
            <li>Seamless Booking: Our intuitive platform makes the booking process simple and efficient.</li>
            <li>Secure Payments: Your transactions are protected with industry-standard security measures.</li>
            <li>Premium Support: Our dedicated customer service team is always ready to assist you.</li>
        </ul>
    """,
    "team_members": [
        {
            "name": "Rahul Sharma",
            "position": "Founder & CEO",
            "bio": "With over 10 years of experience in the event industry, Rahul founded District Events to revolutionize how people discover and book premium events.",
            "image_url": "https://images.unsplash.com/photo-1568602471122-7832951cc4c5"
        },
        {
            "name": "Priya Patel",
            "position": "Chief Experience Officer",
            "bio": "Priya brings her expertise in user experience design to ensure that District Events offers a seamless and enjoyable booking experience.",
            "image_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2"
        },
        {
            "name": "Vikram Singh",
            "position": "Head of Partnerships",
            "bio": "Vikram works closely with venues and event organizers to bring exclusive events to the District Events platform.",
            "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e"
        }
    ]
}

# Data for Contact Us page
contact_data = {
    "title": "Contact Us",
    "description": "We'd love to hear from you! Reach out to us with any questions, feedback, or inquiries.",
    "email": "info@districtevents.com",
    "phone": "+91 1234567890",
    "address": "123 Main Street, Koramangala, Bangalore - 560034, India",
    "social_media": {
        "facebook": "https://facebook.com/districtevents",
        "twitter": "https://twitter.com/districtevents",
        "instagram": "https://instagram.com/districtevents",
        "linkedin": "https://linkedin.com/company/districtevents"
    },
    "office_hours": "Monday to Friday: 9:00 AM - 6:00 PM IST"
}

# Data for Feedback page
feedback_data = {
    "title": "Share Your Feedback",
    "description": "We value your opinion! Help us improve District Events by sharing your thoughts and experiences."
}

@app.route('/')
def index():
    """Redirect to About Us page as default landing page."""
    return redirect(url_for('about'))

@app.route('/about')
def about():
    """Render the About Us page."""
    return render_template('about.html', data=about_data)

@app.route('/contact')
def contact():
    """Render the Contact Us page."""
    return render_template('contact.html', data=contact_data)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Render the Feedback page and process form submissions."""
    if request.method == 'POST':
        # Process feedback form data
        name = request.form.get('name')
        email = request.form.get('email')
        feedback_type = request.form.get('feedback_type')
        message = request.form.get('message')
        newsletter_signup = request.form.get('newsletter_signup') == 'on'

        # In a real application, you would save this data to a database
        # For now, we'll just return a success message

        return render_template('feedback.html', data=feedback_data,
                               success=True,
                               message="Thank you for your feedback! We appreciate your input.")

    # GET request - just render the form
    return render_template('feedback.html', data=feedback_data)

# API Endpoints for integration with Django application
@app.route('/api/about')
def api_about():
    """Return About Us data as JSON for Django to consume."""
    return jsonify({
        "title": about_data["title"],
        "description": about_data["description"],
        "content": about_data["content"],
        "team_members": about_data["team_members"]
    })

@app.route('/api/contact')
def api_contact():
    """Return Contact Us data as JSON for Django to consume."""
    return jsonify(contact_data)

@app.route('/api/feedback', methods=['POST'])
def api_feedback():
    """API endpoint to receive feedback submissions from Django."""
    data = request.json

    # Validate required fields
    if not data.get('name') or not data.get('email') or not data.get('message'):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # In a real application, you would save this data to a database
    # For now, we'll just return a success message

    return jsonify({
        "success": True,
        "message": "Thank you for your feedback! We appreciate your input."
    })

if __name__ == '__main__':
    # Get port from environment variable or use 8000 as default
    port = int(os.environ.get("PORT", 8000))
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=os.environ.get("DEBUG", "True") == "True")