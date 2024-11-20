import unittest
from app import app, db, User

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

if __name__ == '__main__':
    unittest.main()