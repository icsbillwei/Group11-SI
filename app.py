# 1. First, modify app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'  # Keep your existing secret key

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
# Flight Model
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(50), unique=True, nullable=False)
    departure_airport = db.Column(db.String(255), nullable=False)
    arrival_location = db.Column(db.String(255), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    seats = db.Column(db.JSON, nullable=False, default=lambda: generate_seat_map())

def generate_seat_map():
    # Create a default seating map (e.g., 5x4 grid with random occupancy)
    # 1 represents occupied, 0 represents available
    return [[0, 1, 0, 0],
            [0, 0, 0, 1],
            [1, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 0]]



# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = email
            return redirect(url_for('book_flight'))
        
        flash('Invalid email or password', 'error')
        return render_template('login.html')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('signup.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')
            
        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return render_template('signup.html')
        
    return render_template('signup.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email not found', 'error')
            return render_template('forgot_password.html')

        return redirect(url_for('reset_password', email=email))

    return render_template('forgot_password.html')

@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not password:
            flash('Please enter a new password', 'error')
            return render_template('reset_password.html', email=email)

        if not user:
            flash('Invalid reset request', 'error')
            return redirect(url_for('login'))

        user.set_password(password)
        try:
            db.session.commit()
            flash('Password has been reset successfully', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return render_template('reset_password.html', email=email)

    return render_template('reset_password.html', email=email)

@app.route('/search_flights', methods=['POST'])
def search_flights():
    departure_airport = request.form.get('departure_airport')
    arrival_location = request.form.get('arrival_location')
    departure_date = request.form.get('departure_date')

    if not departure_airport or not arrival_location or not departure_date:
        flash('Please provide all required information', 'error')
        return redirect(url_for('book_flight'))

    # Filter flights based on user's criteria
    matching_flights = Flight.query.filter(
        Flight.departure_airport.ilike(departure_airport),
        Flight.arrival_location.ilike(arrival_location),
        db.func.date(Flight.departure_time) == departure_date
    ).all()

    if not matching_flights:
        flash('No flights match your search criteria. Please try again.', 'error')
        return redirect(url_for('book_flight'))

    return render_template('flight_results.html', flights=matching_flights)

@app.route('/payment_method/<int:flight_id>', methods=['GET', 'POST'])
def payment_method(flight_id):
    if request.method == 'POST':
        # Process payment here
        flash('Payment successful! Thank you for your purchase.', 'success')
        return redirect(url_for('book_flight'))

    return render_template('payment_method.html', flight_id=flight_id)

@app.route('/select_seat/<int:flight_id>', methods=['GET', 'POST'])
def select_seat(flight_id):
    flight = Flight.query.get_or_404(flight_id)

    if request.method == 'POST':
        selected_seat = request.form.get('seat')
        row, col = map(int, selected_seat.split(','))

        if flight.seats[row][col] == 0:  # Check if seat is available
            flight.seats[row][col] = 1  # Mark seat as occupied
            db.session.commit()
            return redirect(url_for('payment_method', flight_id=flight_id))
        else:
            flash('Seat is already occupied. Please select another.', 'error')

    return render_template('select_seat.html', flight=flight)



@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

# entry point to the app
@app.route('/book_flight', methods=['GET', 'POST'])
def book_flight():
    if 'email' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    # Fetch distinct airport codes from both departure_airport and arrival_location
    departure_airports = db.session.query(Flight.departure_airport).distinct().all()
    arrival_airports = db.session.query(Flight.arrival_location).distinct().all()

    # Combine and deduplicate the airport codes
    airport_codes = set(code[0] for code in departure_airports + arrival_airports)

    return render_template('book_flight.html', airport_codes=airport_codes)

@app.route('/index')
def index():
    if 'email' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    return render_template('index.html')

# Create database tables
def init_db():
    with app.app_context():
        db.create_all()

    # Check if flights already exist
        if Flight.query.count() == 0:
            # Add some flight data for initialization
            flights = [
                Flight(flight_number="AB123", departure_airport="JFK", arrival_location="LAX",
                       departure_time=datetime(2024, 11, 5, 14, 0), arrival_time=datetime(2024, 11, 5, 17, 30),
                       cost=299.99, seats=generate_seat_map()),
                Flight(flight_number="CD456", departure_airport="JFK", arrival_location="SFO",
                       departure_time=datetime(2024, 11, 6, 16, 0), arrival_time=datetime(2024, 11, 6, 19, 45),
                       cost=349.99, seats=generate_seat_map()),
            ]
            
            db.session.bulk_save_objects(flights)
            db.session.commit()

if __name__ == '__main__':
    init_db()  # Initialize database tables
    app.run(debug=True)