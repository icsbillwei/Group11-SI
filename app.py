"""
Flight Ticket Booking System

This Flask application allows users to create accounts, log in, book flights, 
select seats, and view their booking history. Users can search for flights 
by departure and arrival airports, as well as book and cancel flights. 
The app also includes payment handling for seat bookings and a login system 
with account creation and password reset options.

Input: 
- User credentials (email, password)
- Flight search criteria (departure airport, arrival location, departure date)
- Seat selection (row, column)

Output:
- Flight search results
- Booking confirmations and history

Run Instructions:
1. Ensure Flask and SQLAlchemy are installed.
2. Run `python app.py` to start the server.
3. Access the app via `http://127.0.0.1:5000` in a web browser.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    """
    Represents a user account in the system.

    Attributes:
    - email: unique identifier for the user.
    - password: hashed password for secure authentication.
    - created_at: timestamp of account creation.

    Methods:
    - set_password: hashes and sets the user's password.
    - check_password: verifies the provided password.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hashes and sets the password for secure storage."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the provided password against the stored hash."""
        return check_password_hash(self.password, password)

# Flight Model
class Flight(db.Model):
    """
    Represents a flight in the system.

    Attributes:
    - flight_number: unique identifier for the flight.
    - departure_airport, arrival_location: location details.
    - departure_time, arrival_time: scheduling information.
    - cost: ticket price.
    - seats: seat availability map.
    """
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(50), unique=True, nullable=False)
    departure_airport = db.Column(db.String(255), nullable=False)
    arrival_location = db.Column(db.String(255), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    seats = db.Column(MutableList.as_mutable(JSON), nullable=False)

    def __repr__(self):
        return f'<Flight {self.flight_number}>'

# Booking Model
class Booking(db.Model):
    """
    Represents a flight booking made by a user.

    Attributes:
    - user_email: email of the booking user.
    - flight_id: associated flight ID.
    - seat_row, seat_col: booked seat location.
    - booked_at: booking timestamp.
    - seats: seat label (e.g., 2A).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    seat_row = db.Column(db.Integer, nullable=False)
    seat_col = db.Column(db.Integer, nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)
    seats = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Booking {self.id} - Flight {self.flight_id} Seat {self.seats}>'
    flight = db.relationship('Flight', backref='bookings')
    
    __table_args__ = (
        db.UniqueConstraint('flight_id', 'seat_row', 'seat_col', 
                          name='unique_seat_booking'),
    )

def generate_seat_map():
    """Generates a 5x4 seat availability map for each flight."""
    return [[0 for _ in range(4)] for _ in range(5)]  # 5x4 grid of available seats

@app.route('/', methods=['GET', 'POST'])
def login():
    """Handles user login, verifies credentials, and starts a session."""
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
    """Allows new users to register by providing email and password."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('signup.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')
            
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
    """Handles user requests to reset their password via email."""
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
    """Resets user password for the provided email address."""
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

@app.route('/book_flight')
def book_flight():
    """Displays the flight booking page with search options."""
    if 'email' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    departure_airports = db.session.query(Flight.departure_airport).distinct().all()
    arrival_airports = db.session.query(Flight.arrival_location).distinct().all()
    airport_codes = set(code[0] for code in departure_airports + arrival_airports)

    return render_template('book_flight.html', airport_codes=airport_codes)

@app.route('/search_flights', methods=['POST'])
def search_flights():
    """Searches for flights matching user-provided criteria."""
    departure_airport = request.form.get('departure_airport')
    arrival_location = request.form.get('arrival_location')
    departure_date = request.form.get('departure_date')

    if not all([departure_airport, arrival_location, departure_date]):
        flash('Please provide all required information', 'error')
        return redirect(url_for('book_flight'))

    matching_flights = Flight.query.filter(
        Flight.departure_airport.ilike(departure_airport),
        Flight.arrival_location.ilike(arrival_location),
        db.func.date(Flight.departure_time) == departure_date
    ).all()

    if not matching_flights:
        flash('No flights match your search criteria', 'error')
        return redirect(url_for('book_flight'))

    return render_template('flight_results.html', flights=matching_flights)

@app.route('/payment_method/<int:flight_id>', methods=['GET', 'POST'])
def payment_method(flight_id):
    """Processes payment and confirms seat booking."""
    if request.method == 'POST':
        # Process payment here
        payment_success = True  # Replace with actual payment confirmation logic

        if payment_success:
            # Retrieve seat and flight info from session
            seat_label = session.get('selected_seat')
            user_email = session.get('email')
            flight = Flight.query.get_or_404(flight_id)
            seat_row = session.get('seat_row')
            seat_col = session.get('seat_col')


            # Create a booking record in the database with the seat information
            new_booking = Booking(
                user_email=user_email, 
                flight_id=flight.id, 
                seats=seat_label,
                seat_row=seat_row,
                seat_col=seat_col
            )
            flight.seats[seat_row][seat_col] = 1
            db.session.add(new_booking)
            db.session.commit()

            # Clear session data after successful booking
            session.pop('selected_seat', None)
            session.pop('flight_id', None)

            flash('Payment successful! Your booking has been confirmed.', 'success')
            return redirect(url_for('booking_history'))
        else:
            flash('Payment failed. Please try again.', 'error')

        return redirect(url_for('book_flight'))

    return render_template('payment_method.html', flight_id=flight_id)

@app.route('/select_seat/<int:flight_id>', methods=['GET', 'POST'])
def select_seat(flight_id):
    """Allows user to select available seats for a specific flight."""
    if 'email' not in session:
        return redirect(url_for('login'))

    flight = Flight.query.get_or_404(flight_id)
    
    current_bookings = Booking.query.filter_by(flight_id=flight_id).all()
    updated_seats = generate_seat_map()
    
    for booking in current_bookings:
        updated_seats[booking.seat_row][booking.seat_col] = 1
    
    flight.seats = updated_seats
    db.session.commit()

    if request.method == 'POST':
        selected_seat = request.form.get('seat')
        if not selected_seat:
            return redirect(url_for('select_seat', flight_id=flight_id))
            
        row, col = map(int, selected_seat.split(','))
        # Convert row and col to seat label (e.g., 2A)
        seat_label = f"{row + 1}{chr(65 + col)}"

        # Store selected seat in session temporarily
        session['selected_seat'] = seat_label
        session['flight_id'] = flight.id
        session['seat_row'] = row
        session['seat_col'] = col
        
        try:
            # Check if the seat is already booked
            return redirect(url_for('payment_method', flight_id=flight_id))
        except Exception as e:
            print(e)
            db.session.rollback()
            return redirect(url_for('select_seat', flight_id=flight_id))

    return render_template('select_seat.html', flight=flight)

@app.route('/booking_history')
def booking_history():
    """Displays booking history for the logged-in user."""
    if 'email' not in session:
        return redirect(url_for('login'))
    
    bookings = Booking.query.filter_by(user_email=session['email']).all()
    return render_template('booking_history.html', bookings=bookings)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Allows user to cancel a booking and releases the seat."""
    if 'email' not in session:
        return redirect(url_for('login'))

    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_email != session['email']:
        flash('Unauthorized action', 'error')
        return redirect(url_for('booking_history'))
    
    try:
        # Update the flight's seat map
        flight = Flight.query.get(booking.flight_id)
        flight.seats[booking.seat_row][booking.seat_col] = 0
        
        # Remove the booking
        db.session.delete(booking)
        db.session.commit()
        flash('Booking canceled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred', 'error')
    
    return redirect(url_for('booking_history'))

@app.route('/logout')
def logout():
    """Logs out the user and clears session data."""
    session.pop('email', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

def init_db():
    """Initializes the database and adds sample flight data."""
    with app.app_context():
        db.create_all()
        
        # sample flights
        if Flight.query.count() == 0:
            flights = [
                Flight(
                    flight_number="AB123",
                    departure_airport="JFK",
                    arrival_location="LAX",
                    departure_time=datetime(2024, 11, 5, 14, 0),
                    arrival_time=datetime(2024, 11, 5, 17, 30),
                    cost=299.99,
                    seats=generate_seat_map()
                ),
                Flight(
                    flight_number="CD456",
                    departure_airport="JFK",
                    arrival_location="SFO",
                    departure_time=datetime(2024, 11, 6, 16, 0),
                    arrival_time=datetime(2024, 11, 6, 19, 45),
                    cost=349.99,
                    seats=generate_seat_map()
                )
            ]
            
            db.session.bulk_save_objects(flights)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)