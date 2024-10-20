# Project Setup and Execution Guide

## Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package installer)
- Virtual environment (optional but recommended)

## Installation Steps

1. **Clone the repository** (if using version control like Git):
   ```bash
   git clone https://github.com/icsbillwei/cisc327-group11.git
   cd cisc327-group11
   ```
2. **Set up a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```
3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. **Start the Flask server:**
    ```bash
    python app.py
    ```
The server should start at http://127.0.0.1:5000/ by default. You can now access the application in your web browser.

## Running the Test Scripts

1. **Ensure the Flask application is not running** (the test client will handle server initialization).
2. **Execute the test suite:**
    ```bash
    python -m unittest test_app.py
    ```
This will run the test cases defined in 'test_app.py' and provide output indicating which tests passed or failed.

## Test Descriptions

- **test_login_valid_credentials**: Tests if a user can log in with valid credentials.
- **test_login_invalid_password**: Tests login failure when an incorrect password is provided.
- **test_signup_success**: Tests successful user signup with all required fields.
- **test_signup_missing_fields**: Tests that signup fails if fields are missing.
- **test_forgot_password_email_already_exists**: Tests if the system correctly processes an existing email for password recovery.
- **test_forgot_password_email_not_exist**: Tests if the system identifies a non-existent email during password recovery.