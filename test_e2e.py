import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Set up the WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument('--lang=en-US')  # Set locale to US English for consistent behavior
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def test_user_signup_and_login(driver, baseURL):
    """Test that a user can sign up and then log in with the same credentials."""
    print("# Test 1: User Signup and Login Test")

    try:
        # Step 1: Navigate to the Signup Page
        driver.get(f"{baseURL}/signup")
        print("Opened signup page.")
        time.sleep(1)  # Pause for visualization

        # Step 2: Sign Up with New User Credentials
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("seleniumuser@example.com")
        password_input.send_keys("password123")
        time.sleep(1)  # Pause for visualization
        password_input.send_keys(Keys.RETURN)
        print("Signed up with new user credentials.")
        time.sleep(1)  # Pause for visualization

        # Step 3: Log In with the Same Credentials
        driver.get(baseURL)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("seleniumuser@example.com")
        password_input.send_keys("password123")
        time.sleep(1)  # Pause for visualization
        password_input.send_keys(Keys.RETURN)
        print("Logged in with the same credentials.")
        time.sleep(1)  # Pause for visualization

        # Step 4: Verify Successful Login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_source = driver.page_source
        if "Book a Flight" in page_source:
            print("Login successful, redirected to 'Book a Flight' page.")
        else:
            print("Login failed or redirection did not occur.")
        time.sleep(1)  # Pause for visualization
    except Exception as e:
        print(f"An error occurred during signup and login test: {e}")

def test_search_and_book_flight(driver, baseURL):
    """Test searching and booking a valid flight."""
    print("# Test 2: Search and Book a Valid Flight Test")

    try:
        # Step 1: Log in with existing user credentials
        driver.get(baseURL)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("seleniumuser@example.com")
        password_input.send_keys("password123")
        password_input.send_keys(Keys.RETURN)
        print("Logged in with existing user credentials.")
        time.sleep(1)  # Pause for visualization

        # Step 2: Navigate to the Book Flight Page
        driver.get(f"{baseURL}/book_flight")
        print("Opened book flight page.")
        time.sleep(1)  # Pause for visualization

        # Step 3: Search for a valid flight
        departure_airport_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "departure_airport"))
        )
        arrival_location_input = driver.find_element(By.NAME, "arrival_location")
        departure_date_input = driver.find_element(By.NAME, "departure_date")
        departure_airport_input.send_keys("JFK")
        arrival_location_input.send_keys("LAX")
        driver.execute_script("arguments[0].value = '2024-11-05';", departure_date_input) # November 5, 2024
        time.sleep(2)  # Pause for visualization
        departure_date_input.send_keys(Keys.RETURN)
        print("Searched for a valid flight.")
        time.sleep(1)  # Pause for visualization

        # Step 4: Verify Search Results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_source = driver.page_source
        if "Flight Results" in page_source:
            print("Flight search successful, results displayed.")
        else:
            print("Flight search failed or no results found.")
        time.sleep(1)  # Pause for visualization
    except Exception as e:
        print(f"An error occurred during search and book flight test: {e}")

def test_successfully_book_flight(driver, baseURL):
    """Test the full flow of booking a flight successfully."""
    print("# Test 3: Successfully Book a Flight Test")

    try:
        # Step 1: Log in with existing user credentials
        driver.get(baseURL)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("seleniumuser@example.com")
        password_input.send_keys("password123")
        password_input.send_keys(Keys.RETURN)
        print("Logged in with existing user credentials.")
        time.sleep(1)  # Pause for visualization

        # Step 2: Navigate to the Book Flight Page
        driver.get(f"{baseURL}/book_flight")
        print("Opened book flight page.")
        time.sleep(1)  # Pause for visualization

        # Step 3: Search for a valid flight
        departure_airport_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "departure_airport"))
        )
        arrival_location_input = driver.find_element(By.NAME, "arrival_location")
        departure_date_input = driver.find_element(By.NAME, "departure_date")
        departure_airport_input.send_keys("JFK")
        arrival_location_input.send_keys("LAX")
        driver.execute_script("arguments[0].value = '2024-11-05';", departure_date_input)  # November 5, 2024
        time.sleep(1)  # Pause for visualization
        departure_date_input.send_keys(Keys.RETURN)
        print("Searched for a valid flight.")
        time.sleep(1)  # Pause for visualization

        # Step 4: Select a flight from the search results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "btn"))
        )
        select_seat = driver.find_element(By.CLASS_NAME, "btn")
        select_seat.click()
        print("Navigated to the 'Select Seats' page.")
        time.sleep(1)  # Pause for visualization

        # Step 5: Select a seat
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "seat"))
        )
        available_seats = driver.find_elements(By.CLASS_NAME, "seat.available")
        if available_seats:
            available_seats[0].click()  # Select the first available seat
            print("Selected the first available seat.")
        else:
            print("No available seats found.")
            return
        time.sleep(1)  # Pause for visualization

        # Step 6: Confirm booking details
        confirm_booking_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "confirm-button"))
        )
        confirm_booking_button.click()
        print("Confirmed booking details.")
        time.sleep(1)  # Pause for visualization

        # Step 7: Enter valid card details
        card_number_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "card-number"))
        )
        expiry_date_input = driver.find_element(By.ID, "expiry-date")
        cvv_input = driver.find_element(By.ID, "cvv")

        card_number_input.send_keys("1234567812345678")  # Example valid card number
        expiry_date_input.send_keys("12/25")  # Example valid expiry date (December 2025)
        cvv_input.send_keys("123")  # Example valid CVV
        print("Entered valid card details.")

        # Step 8: Click the Confirm Payment button
        confirm_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        confirm_button.click()
        print("Clicked Confirm Payment button.")

        # Step 9: Verify Booking Success
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_source = driver.page_source
        if "Booking History" in page_source:
            print("Flight booking successful.")
        else:
            print("Flight booking failed or confirmation not displayed.")
        time.sleep(1)  # Pause for visualization

    except Exception as e:
        print(f"An error occurred during the flight booking test: {e}")

if __name__ == "__main__":
    driver = setup_driver()
    baseURL = "http://127.0.0.1:5000"

    try:
        test_user_signup_and_login(driver, baseURL)
        test_search_and_book_flight(driver, baseURL)
        test_successfully_book_flight(driver, baseURL)
    finally:
        driver.quit()