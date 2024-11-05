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

On the first run, the application will automatically create a users.db database with sample flights.

The server should start at 'http://127.0.0.1:5000/' by default. You can now access the application in your web browser.

## Usage Guide

1. **Sign Up:** Create an account at /signup.
2. **Log In:** Log into your account at /.
3. **Book a Flight:** Navigate to /book_flight to search for available flights by selecting departure and arrival locations.
4. **Select a Seat:** Choose a seat on the flight after selecting a flight.
5. **Payment:** Complete your booking by entering payment information.
6. **View Booking History:** Review all booked flights at /booking_history.
7. **Cancel Booking:** If needed, cancel a flight booking from the booking history page.

## Sample Flights

The following sample flights are preloaded into the system upon the first run:
1.	**Flight AB123** 
    * **Departure**: JFK 
    * **Arrival**: LAX 
    * **Departure Time**: Nov 5, 2024, 14:00 
    * **Arrival Time**: Nov 5, 2024, 17:30 
    * **Cost**: $299.99”
2. **Flight CD456** 
    * **Departure**: JFK 
    * **Arrival**: SFO 
    * **Departure Time**: Nov 6, 2024, 16:00 
    * **Arrival Time**: Nov 6, 2024, 19:45 
    * **Cost**: $349.99”

## Running the Test Scripts

**Important**: Before running the test script, delete the `users.db` database file to ensure a clean database state. 
   ```bash
   rm -f instance/users.db
   ```
Then, follow these steps:
1. **Ensure the Flask application is not running** (the test client will handle server initialization).
2. **Execute the test suite:**
    ```bash
    python -m unittest test_app.py
    ```
This will run the test cases defined in 'test_app.py' and provide output indicating which tests passed or failed.

## Test Descriptions

### Authentication Tests 
1. **`test_01_login_valid_credentials`**: Verifies that a user can log in with valid credentials. 
2. **`test_02_login_invalid_password`**: Ensures that a login attempt with an invalid password is unsuccessful and returns an appropriate error message.
3. **`test_03_signup_success`**: Tests that a new user can successfully sign up with a unique email.
4. **`test_04_signup_existing_email`**: Checks that signing up with an already registered email results in an error.

### Password Reset Tests 
5. **`test_05_reset_password_success`**: Verifies that a user can reset their password successfully. 
6. **`test_06_reset_password_no_password`**: Ensures that the password reset fails if no new password is provided.

### Booking Flow Tests 
7. **`test_07_book_flight_success`**: Confirms that a logged-in user can access the flight booking page. 
8. **`test_08_search_flights`**: Verifies that searching for flights with valid criteria returns matching flight results.
9. **`test_09_search_flights_no_results`**: Ensures that a search with no matching flights returns an appropriate message. 
10. **`test_10_select_seat`**: Checks that a user can select a seat for a specified flight and proceed to the payment page.
11. **`test_11_payment_method_success`**: Simulates a successful payment process, confirming that the booking is completed.

### Booking Management Tests 
12. **`test_12_booking_history`**: Verifies that a logged-in user can view their booking history and see their booked flights.
13. **`test_13_cancel_booking`**: Tests that a user can cancel an existing booking and receives a confirmation.

### Logout Test 
14. **`test_14_logout`**: Confirms that a user can log out successfully and receives a logout confirmation.

## Project Structure

* **app.py**: Main application file containing route definitions and application logic
* **templates/**: Contains HTML templates for different pages (e.g., login, signup, booking, etc.). 
* **static/**: Holds static files, including images, CSS, and JavaScript.
* **requirements.txt**: Lists the required dependencies for the project. 
* **test_app.py**: Contains the test cases to verify the functionality of the application.

## Additional Information

For more details on each page and its components, refer to the HTML files in the `templates/` directory, which include the layout and structure for pages such as:
* **Login** (`login.html`) 
* **Sign Up** (`signup.html`) 
* **Forgot Password** (`forgot_password.html`) 
* **Reset Password** (`reset_password.html`) 
* **Flight Search** (`book_flight.html`) 
* **Flight Results** (`flight_results.html`)
* **Seat Selection** (`select_seat.html`) 
* **Payment** (`payment_method.html`) 
* **Booking History** (`booking_history.html`)
