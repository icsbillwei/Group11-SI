import unittest
from flask import Flask
from app import app, db, User
from werkzeug.security import generate_password_hash

class FlaskAuthTests(unittest.TestCase):

    def setUp(self):
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

    def tearDown(self):
        # Clear users after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login_valid_credentials(self):
        # Verify if a user will be able to login with a valid email and password
        response = self.app.post('/', data={
            'email': self.test_email,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_password(self):
        # Verify if a user cannot login with a valid email and an invalid password
        response = self.app.post('/', data={
            'email': self.test_email,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)

    def test_signup_success(self):
        # Verify if a user can sign up successfully
        response = self.app.post('/signup', data={
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully', response.data)

    def test_signup_existing_email(self):
        # Verify if signing up with an existing email triggers an error
        response = self.app.post('/signup', data={
            'email': self.test_email,
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Email already exists', response.data)

    def test_reset_password_success(self):
        # Verify if a user can successfully reset their password
        response = self.app.post(f'/reset_password/{self.test_email}', data={
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Password has been reset successfully', response.data)

    def test_reset_password_no_password(self):
        # Verify if a user cannot reset their password without providing a new password
        response = self.app.post(f'/reset_password/{self.test_email}', data={
            'password': ''
        }, follow_redirects=True)
        self.assertIn(b'Please enter a new password', response.data)
    
    def test_search_flights_success(self):
        # Verify if flight search returns results for valid search criteria
        response = self.app.post('/search_flights', data={
            'departure_airport': 'JFK',
            'arrival_location': 'LAX',
            'departure_date': '2024-11-05'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_search_flights_missing_fields(self):
        # Verify if the user receives an error when search fields are missing
        response = self.app.post('/search_flights', data={
            'departure_airport': 'JFK',
            'arrival_location': '',
            'departure_date': '2024-11-05'
        }, follow_redirects=True)
        self.assertIn(b'Please provide all required information', response.data)

    def test_logout(self):
        # Verify if a user can successfully logout
        with self.app.session_transaction() as session:
            session['email'] = self.test_email  # Simulate a logged-in user
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', response.data)

    def test_book_flight_redirect_if_not_logged_in(self):
        # Verify if a non-logged-in user is redirected to the login page
        response = self.app.get('/book_flight', follow_redirects=True)
        self.assertIn(b'Please login first', response.data)

    def test_book_flight_success(self):
        # Verify if a logged-in user can access the booking page
        with self.app.session_transaction() as session:
            session['email'] = self.test_email  
        response = self.app.get('/book_flight', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
