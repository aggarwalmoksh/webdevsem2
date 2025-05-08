# Event Management System

## Overview

The **Event Management System** is a web application designed for event booking and management. It allows users to book events, and admins can create, manage, and organize events. The system features user authentication and integrates a Flask application for the "Contact Us" and "About Us" pages, which are connected via REST APIs to the Django application.

---

## Features

- **Event Booking**: Users can browse available events and book them.
- **User Authentication**: Secure login and registration for users to manage their bookings.
- **Admin Panel**: Admin users can create, edit, and delete events.
- **Contact Us**: A Flask-based "Contact Us" page where users can reach out for support.
- **About Us**: A Flask-based "About Us" page that provides information about the platform.
- **REST API Integration**: Flask application is connected to the Django app using REST APIs for communication between the services.

---

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Django (for event management), Flask (for contact and about us features)
- **Database**: SQLite
- **Communication**: REST API for connecting Flask and Django applications

---

## Installation Instructions

### Prerequisites

- Ensure you have **Python** installed (version 3.6 or above).
- Install **pip** for managing Python dependencies.

### Steps to Set Up

1. **Clone the repository** to your local machine:
   ```bash
   git clone <repository-url>
2. **Navigate to both the Django and Flask directories** and install the required dependencies for both applications by running the following command in each folder:
   ```bash
   pip install -r requirements.txt
3. **Set up the Django application**:
    1. Navigate to the Django root folder:
       ```bash
       cd <django-root-folder>

    2. Apply database migrations:
       ```bash
       python manage.py migrate

    3. Start the Django development server:
       ```bash
       python manage.py runserver

4. **Set up the Flask application**:
    1. Navigate to the Flask application folder:
       ```bash
       cd <flask-folder>

    2. Set the FLASK_APP environment variable:
       ```bash
       export FLASK_APP=app.py  # On Windows, use `set FLASK_APP=app.py`

    3. Start the Flask server:
       ```bash
       flask run

Now, both the Django application and Flask application should be running locally.

## Usage Instructions

### Django Application:
  Access the Django application through your browser at:
  http://127.0.0.1:8000
  Users can browse events, register/login, and book events.
  Admins can create and manage events through the admin panel.

### Flask Application:

  Access the Flask application through your browser at:
  http://127.0.0.1:5000
  The Contact Us and About Us pages are available here, integrated via API with the Django backend.

## Credits and Acknowledgments
  ### Moksh Aggarwal (Team Leader)
  #### Mayur Mittal
  #### Mayank Singh
  #### Madhav Sharma

  
  ### Ratan Lal Gupta (Assistant Professor)

## Project Status
The Event Management System is currently still in development and is being built for college evaluation purposes.

## License
This project is being developed for educational purposes and is not licensed for commercial use.
