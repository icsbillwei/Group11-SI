import unittest
from unittest.mock import patch
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

    def test_15_login_missing_email(self):
        """Test login with missing email or password."""
        print("Running login with missing email test")
        # Test login without email
        response = self.app.post('/', data={'email': '', 'password': self.test_password}, follow_redirects=True)
        self.assertIn(b'Please provide both email and password', response.data)
        print("Login with missing email test completed successfully")

    def test_16_login_missing_password(self):
        """Test login with an invalid email format."""
        print("Running login with missing password test")
        # Test login without password
        response = self.app.post('/', data={'email': self.test_email, 'password': ''}, follow_redirects=True)
        self.assertIn(b'Please provide both email and password', response.data)
        print("Login with missing passwords format test completed successfully")

    def test_17_forgot_password_nonexistent_email(self):
        """Test forgot password with a non-existing email."""
        print("Running forgot password with non-existing email test")
        # Test forgot password with an email that doesn't exist in the database
        response = self.app.post('/forgot_password', data={'email': 'nonexistent@example.com'}, follow_redirects=True)
        self.assertIn(b'Email not found', response.data)
        print("Forgot password with non-existing email test completed successfully")

    def test_18_session_timeout(self):
        """Test access to protected routes after session timeout."""
        print("Running session timeout test")
        # Set up the session and then simulate logout
        with self.app.session_transaction() as session:
            session['email'] = self.test_email
        self.app.get('/logout', follow_redirects=True)
        # Attempt to access a protected route
        response = self.app.get('/book_flight', follow_redirects=True)
        self.assertIn(b'Please login first', response.data)
        print("Session timeout test completed successfully")

    def test_19_signup_missing_password(self):
        """Test signup with missing password."""
        print("Running sign with missing password test")
        # Test signup without password
        response = self.app.post('/', data={'email': self.test_email, 'password': ''}, follow_redirects=True)
        self.assertIn(b'Please provide both email and password', response.data)
        print("Signup with missing passwords format test completed successfully")

    def test_20_signup_database_error(self):
        """Test signup route handling a database exception."""
        print("Running signup database exception test")
        with patch('app.db.session.commit', side_effect=Exception("Database error")):
            # Attempt to sign up with valid data
            response = self.app.post('/signup', data={
                'email': 'erroruser@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            # Check if the rollback was triggered and the error message is flashed
            self.assertIn(b'An error occurred', response.data)
        print("Signup database exception test completed successfully")

    def test_21_reset_password_database_error(self):
        """Test reset password route handling a database exception."""
        print("Running reset password database exception test")
        with patch('app.db.session.commit', side_effect=Exception("Database error")):
            # Attempt to reset the password with valid data
            response = self.app.post(f'/reset_password/{self.test_email}', data={
                'password': 'newpassword123'
            }, follow_redirects=True)
            
            # Check if the rollback was triggered and the error message is flashed
            self.assertIn(b'An error occurred', response.data)
        print("Reset password database exception test completed successfully")

    def test_22_select_seat_exception_handling(self):
        """Test exception handling during seat selection."""
        print("Running select seat exception handling test")
        with patch('app.db.session.commit', side_effect=Exception("Database error")):
            with self.app.session_transaction() as session:
                session['email'] = self.test_email
            response = self.app.post(f'/select_seat/{self.test_flight.id}', data={
                'seat': '1,1'
            }, follow_redirects=True)
            # Check if the error message is flashed and the user is redirected to the flight search page
            self.assertEqual(response.status_code, 500)
        print("Select seat exception handling test completed successfully")

    def test_23_cancel_booking_exception_handling(self):
        """Test exception handling during booking cancellation."""
        print("Running cancel booking exception handling test")
        # First, create a test booking to attempt to cancel
        with app.app_context():
            test_booking = Booking(
                user_email=self.test_email,
                flight_id=self.test_flight.id,
                seats="2B",
                seat_row=1,
                seat_col=1
            )
            db.session.add(test_booking)
            db.session.commit()
            booking_id = test_booking.id

        # Patch the db.session.commit to raise an exception to simulate a failure
        with patch('app.db.session.commit', side_effect=Exception("Database error")):
            with self.app.session_transaction() as session:
                session['email'] = self.test_email
            
            # Attempt to cancel the booking, which should raise an exception and trigger rollback
            response = self.app.post(f'/cancel_booking/{booking_id}', follow_redirects=True)
            
            # Check if the rollback was triggered and the error message is flashed
            self.assertIn(b'An error occurred', response.data)
            # Check if the user is redirected to the booking history page
            self.assertIn(b'<title>Booking History</title>', response.data)
        print("Cancel booking exception handling test completed successfully")
    def test_24_reset_password_invalid_user(self):
        """Test invalid reset password request with a non-existent user."""
        print("Running reset password invalid user test")
        # Attempt to reset password for an email that does not exist
        response = self.app.post('/reset_password/nonexistent@example.com', data={
            'password': 'newpassword123'
        }, follow_redirects=True)
        
        # Check that the error message is flashed and user is redirected to login
        self.assertIn(b'Invalid reset request', response.data)
        self.assertIn(b'<title>Login</title>', response.data)  # Confirm redirection to login
        print("Reset password invalid user test completed successfully")

    def test_25_search_flights_missing_information(self):
        """Test searching flights with missing required information."""
        print("Running search flights missing information test")
        
        # Test missing departure_airport
        response = self.app.post('/search_flights', data={
            'departure_airport': '',
            'arrival_location': 'LAX',
            'departure_date': '2024-11-05'
        }, follow_redirects=True)
        self.assertIn(b'Please provide all required information', response.data)
        print("Search flights missing information test completed successfully")
    
    def test_26_access_protected_route_without_login(self):
        """Test accessing a protected route without being logged in."""
        print("Running protected route access without login test")
        # Attempt to access the book flight page without being logged in
        response = self.app.get('/book_flight', follow_redirects=True)

        # Check for redirection to login page
        self.assertIn(b'Please login first', response.data)
        self.assertIn(b'<title>Login</title>', response.data)
        print("Protected route access without login test completed successfully")
    
    def test_27_cancel_booking_unauthorized(self):
        """Test unauthorized booking cancellation attempt."""
        print("Running unauthorized booking cancellation test")

        # Create a booking for a different user
        with app.app_context():
            another_user_email = 'otheruser@example.com'
            other_user = User(email=another_user_email)
            other_user.set_password('password123')
            db.session.add(other_user)
            db.session.commit()

            # Book a seat for the other user
            other_booking = Booking(
                user_email=another_user_email,
                flight_id=self.test_flight.id,
                seats="3C",
                seat_row=2,
                seat_col=2
            )
            db.session.add(other_booking)
            db.session.commit()
            booking_id = other_booking.id

        # Log in as the test user and attempt to cancel the other user's booking
        with self.app.session_transaction() as session:
            session['email'] = self.test_email
        
        response = self.app.post(f'/cancel_booking/{booking_id}', follow_redirects=True)

        # Check for unauthorized action flash message and redirection to booking history
        self.assertIn(b'Unauthorized action', response.data)
        self.assertIn(b'<title>Booking History</title>', response.data)
        print("Unauthorized booking cancellation test completed successfully")

if __name__ == '__main__':
    unittest.main()
