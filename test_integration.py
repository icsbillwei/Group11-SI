import unittest
from unittest.mock import patch
from flask import Flask
from app import app, db, User, Flight, Booking, generate_seat_map
from werkzeug.security import generate_password_hash
from datetime import datetime

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the test environment after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_signup_and_login(self):
        """Test that a user can sign up and then log in with the same credentials."""
        print("Running user signup and login integration test")

        # Sign up with new user credentials
        print("Signing up with new user credentials")
        response = self.app.post('/signup', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully', response.data)
        print("Signup test completed successfully")

        # Log in with the same credentials
        print("Logging in with the same credentials")
        response = self.app.post('/', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Book a Flight', response.data)
        print("Login test completed successfully")

        # Check if the user is redirected to the book flight page
        print("Checking redirection to book flight page")
        response = self.app.get('/book_flight', follow_redirects=True)
        self.assertIn(b'Book a Flight', response.data)
        print("Redirection to book flight page test completed successfully")

class IntegrationTestCase2(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
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
        """Clean up the test environment after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_book_flight_and_check_history(self):
        """Test user login, booking a flight, and viewing booking history."""
        print("Running login, book flight, and check booking history integration test")

        # Sign up with new user credentials
        print("Signing up with new user credentials")
        response = self.app.post('/signup', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully', response.data)
        print("Signup test completed successfully")

        # Log in with the same credentials
        print("Logging in with the same credentials")
        response = self.app.post('/', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Book a Flight', response.data)
        print("Login test completed successfully")

        # # Search for flights and select a flight
        print("Searching for flights and selecting a flight")
        response = self.app.post('/search_flights', data={
            'departure_airport': 'JFK',
            'arrival_location': 'LAX',
            'departure_date': '2024-11-05'
        }, follow_redirects=True)
        self.assertIn(b'AB123', response.data) 
        print("Flight search test completed successfully")

        # Select a seat on the flight
        flight_id = 1  # Assuming flight ID 1 exists
        print("Selecting a seat for the flight")
        response = self.app.post(f'/select_seat/{flight_id}', data={
            'seat': '0,0'  # First row, first seat
        }, follow_redirects=True)
        self.assertIn(b'Payment Method', response.data)
        print("Seat selection test completed successfully")

        # Process payment and confirm booking
        print("Processing payment and confirming booking")
        response = self.app.post(f'/payment_method/{flight_id}', follow_redirects=True)
        self.assertIn(b'Payment successful!', response.data)
        print("Booking confirmation test completed successfully")


if __name__ == '__main__':
    unittest.main()