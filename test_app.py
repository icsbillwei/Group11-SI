import unittest
from flask import Flask
from werkzeug.security import generate_password_hash
from app import app, users

class FlaskAuthTests(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

        # Add a test user
        self.test_email = 'test@example.com'
        self.test_password = 'password123'
        users[self.test_email] = {
            'password': generate_password_hash(self.test_password)
        }

    def tearDown(self):
        # Clear users after each test
        users.clear()

    def test_login_valid_credentials(self):
        # Verify if a user will be able to login with a valid username and valid password
        response = self.app.post('/', data={
            'email': self.test_email,
            'password': self.test_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_password(self):
        # Verify if a user cannot login with a valid username and an invalid password
        response = self.app.post('/', data={
            'email': self.test_email,
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)
        
    def test_signup_success(self):
        # Verify if a user can sign-up successfully with all the mandatory details
        response = self.app.post('/signup', data={
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }, follow_redirects=True)
        self.assertIn(b'Account created successfully', response.data)

    def test_signup_missing_fields(self):
        # Verify if the user cannot proceed without filling all the mandatory fields at registration
        response = self.app.post('/signup', data={
            'email': 'incomplete@example.com',
            'password': ''
        }, follow_redirects=True)
        self.assertIn(b'Please provide both email and password', response.data)

    def test_forgot_password_email_already_exists(self):
        # Verify if the application identifies an existing email correctly during password recovery
        response = self.app.post('/forgot_password', data={
            'email': self.test_email,
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_email_not_exist(self):
        # Verify if the application identifies a non-existing email correctly during password recovery
        response = self.app.post('/forgot_password', data={
            'email': 'nonexistent@example.com',
        }, follow_redirects=True)
        self.assertIn(b'Email not found', response.data)

if __name__ == '__main__':
    unittest.main()
