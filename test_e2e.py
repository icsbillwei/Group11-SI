import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Set up the WebDriver."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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
        departure_date_input.send_keys("11052024") # November 5, 2024
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

if __name__ == "__main__":
    driver = setup_driver()
    baseURL = "http://127.0.0.1:5000"

    try:
        test_user_signup_and_login(driver, baseURL)
        test_search_and_book_flight(driver, baseURL)
    finally:
        driver.quit()