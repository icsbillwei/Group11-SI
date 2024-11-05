import unittest
from flask import Flask
from app import app, db, User, Flight, Booking, generate_seat_map
from werkzeug.security import generate_password_hash
from datetime import datetime

class FlaskAuthTests(unittest.TestCase):
    """
    Unit tests for the Flask-based Flight Booking Application.
    
    Tests cover user authentication, booking, flight search, seat selection, 
    and booking history. They ensure key app functions work as expected,
    including successful login, signup, booking confirmation, and cancellation.
    """

    def setUp(self):
        """
        Set up test environment and initialize test data.
        
        Creates a test client, initializes an in-memory database,
        and populates it with sample user and flight data.
        """
        # Set up the test client and database
        self.app = app.test_client()
        self.app.testing = True

        # Create a test database
        with app.app_context():
            db.create_all()
            # Add a test user to the database
            self.test_email = 'test@example.com'
            self.test_password = 'password123'
            test_user = User(email=self.test_email)
            test_user.set_password(self.test_password)
            db.session.add(test_user)
            db.session.commit()

            test_flight = Flight(
                flight_number="AB123",
                departure_airport="JFK",
                arrival_location="LAX",
                departure_time=datetime(2024, 11, 5, 14, 0),
                arrival_time=datetime(2024, 11, 5, 17, 30),
                cost=299.99,
                seats=generate_seat_map()
            )
            db.session.add(test_flight)
            db.session.commit()

            self.test_flight = Flight.query.filter_by(flight_number="AB123").first()

    def tearDown(self):
        """
        Clean up after each test.
        
        Drops all tables and clears the test database after each test case.
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_login_valid_credentials(self):
        """Test login with valid credentials."""
        print("Running valid login test")
        # Verify if a user will be able to login with a valid email and password
        response = self.app.post('/', data={
            'email': self.test_email,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("Valid login test completed successfully")

    def test_02_login_invalid_password(self):
        """Test login with valid email but invalid password."""
        print("Running invalid login test")
        # Verify if a user cannot login with a valid email and an invalid password
        response = self.app.post('/', data={
            'email': self.test_email,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)
        print("Invalid login test completed successfully")

    def test_03_signup_success(self):
        """Test successful signup with a new user email."""
        print("Running signup success test")
        # Verify if a user can sign up successfully
        response = self.app.post('/signup', data={
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully', response.data)
        print("Signup success test completed successfully")

    def test_04_signup_existing_email(self):
        """Test signup with an already existing user email."""
        print("Running signup with existing email test")
        # Verify if signing up with an existing email triggers an error
        response = self.app.post('/signup', data={
            'email': self.test_email,
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Email already exists', response.data)
        print("Running signup with existing email test completed successfully")

    def test_05_reset_password_success(self):
        """Test successful password reset."""
        print("Running reset password success test")
        # Verify if a user can successfully reset their password
        response = self.app.post(f'/reset_password/{self.test_email}', data={
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Password has been reset successfully', response.data)
        print("Reset password success test completed successfully")

    def test_06_reset_password_no_password(self):
        """Test reset password without providing a new password."""
        print("Running reset password without password test")
        # Verify if a user cannot reset their password without providing a new password
        response = self.app.post(f'/reset_password/{self.test_email}', data={
            'password': ''
        }, follow_redirects=True)
        self.assertIn(b'Please enter a new password', response.data)
        print("Reset password without password test completed successfully")

    def test_07_book_flight_success(self):
        """Test accessing the flight booking page as a logged-in user."""
        print("Running book flight page success test")
        # Verify if a logged-in user can access the booking page
        with self.app.session_transaction() as session:
            session['email'] = self.test_email  
        response = self.app.get('/book_flight', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("Book flight page success test completed successfully")

    def test_08_search_flights(self):
        """Test searching for flights with available results."""
        print("Running search flights with results test")
        # Verify that a flight with available seats appears in search results
        response = self.app.post('/search_flights', data={
            'departure_airport': 'JFK',
            'arrival_location': 'LAX',
            'departure_date': '2024-11-05'
        }, follow_redirects=True)
        self.assertIn(b'AB123', response.data)  # Flight number should appear in search results
        print("Search flights with results test completed successfully")

    def test_09_search_flights_no_results(self):
        """Test searching for flights with no matching results."""
        print("Running search flights with no results test")
        # Verify that no results are returned when there are no flights available
        response = self.app.post('/search_flights', data={
            'departure_airport': 'JFK',
            'arrival_location': 'LAX',
            'departure_date': '2024-11-06'
        }, follow_redirects=True)
        self.assertIn(b'No flights match your search criteria', response.data)
        print("Search flights with no results test completed successfully")

    def test_10_select_seat(self):
        """Test selecting a seat for a specified flight."""
        print("Running select seat test")
        # Verify that a user can select a seat for a flight
        with self.app.session_transaction() as session:
            session['email'] = self.test_email     
        response = self.app.post(f'/select_seat/{self.test_flight.id}', data={
            'seat': '1,1'  # Attempt to select seat in row 1, column 1
        }, follow_redirects=True)
        # Check that the selection redirects to the payment method page
        self.assertEqual(response.status_code, 200)
        print("Select seat test completed successfully")

    def test_11_payment_method_success(self):
        """Test payment processing and booking confirmation."""
        print("Running payment method success test")
        # Verify that a user can successfully complete payment and book a flight
        with self.app.session_transaction() as session:
            session['email'] = self.test_email 
            session['selected_seat'] = "2B"
            session['seat_row'] = 1
            session['seat_col'] = 1
            session['flight_id'] = self.test_flight.id
        # Simulate payment success
        response = self.app.post(f'/payment_method/{self.test_flight.id}', data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("Payment method success test completed successfully")

    def test_12_booking_history(self):
        """Test accessing booking history for logged-in user."""
        print("Running booking history test")
        # Verify that a user can access their booking history
        with self.app.session_transaction() as session:
            session['email'] = self.test_email
        # Create a test booking for the user
        with app.app_context():
            new_booking = Booking(
                user_email=self.test_email,
                flight_id=self.test_flight.id,
                seats="2B",
                seat_row=1,
                seat_col=1
            )
            db.session.add(new_booking)
            db.session.commit()
        # Access booking history page
        response = self.app.get('/booking_history', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'2B', response.data)  # Verify booking appears in the history
        print("Booking history test completed successfully")

    def test_13_cancel_booking(self):
        """Test canceling a booking by the logged-in user."""
        print("Running cancel booking test")
        # Verify that a user can cancel a booking
        with self.app.session_transaction() as session:
            session['email'] = self.test_email # Log in the user
        # Create a test booking to be canceled
        with app.app_context():
            booking = Booking(
                user_email=self.test_email,
                flight_id=self.test_flight.id,
                seats="2B",
                seat_row=1,
                seat_col=1
            )
            db.session.add(booking)
            db.session.commit()
            booking_id = booking.id
        # Send POST request to cancel the booking
        response = self.app.post(f'/cancel_booking/{booking_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Booking canceled successfully', response.data)
        print("Cancel booking test completed successfully")

    def test_14_logout(self):
        """Test user logout functionality."""
        print("Running logout test")
        # Verify if a user can successfully logout
        with self.app.session_transaction() as session:
            session['email'] = self.test_email 
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out', response.data)
        print("Logout test completed successfully")

if __name__ == '__main__':
    unittest.main()