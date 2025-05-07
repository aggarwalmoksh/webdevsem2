from flask import render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from . import admin_bp, events_bp
from .. import db 
from ..admin.routes import admin_required, is_admin_logged_in 


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'

@admin_bp.route('/login', methods=['GET'])
def login():
    return render_template('admin/login.html')

@admin_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    error = None

    admin = Admin.query.filter_by(username=username).first()

    if admin is None or not check_password_hash(admin.password, password):
        error = 'Invalid username or password'
        flash(error)
        return redirect(url_for('admin.login'))
    else:
        session['admin_id'] = admin.id
        flash('Logged in successfully!')
        return redirect(url_for('events.list_events')) 

    return render_template('admin/login.html')

def is_admin_logged_in():
    return 'admin_id' in session

# Example decorator to protect admin routes
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Event {self.title}>'

@events_bp.route('/')
def list_events():
    events = Event.query.all()
    is_admin = is_admin_logged_in()
    return render_template('events/event_list.html', events=events, is_admin=is_admin)

@events_bp.route('/api/admin/events/<int:event_id>', methods=['PUT', 'PATCH'])
@admin_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    try:
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        db.session.commit()
        return jsonify({'message': 'Event updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating event: {str(e)}'}), 500

@events_bp.route('/api/admin/events/<int:event_id>', methods=['DELETE'])
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting event: {str(e)}'}), 500

@events_bp.route('/api/events')
def get_all_events():
    events = Event.query.all()
    event_list = [{'id': event.id, 'title': event.title, 'description': event.description} for event in events]
    return jsonify(event_list)