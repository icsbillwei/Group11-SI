from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_user_signup_and_login():
    # Set up the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    baseURL = "http://127.0.0.1:5000"

    print("# Test 1: User Signup and Login Test")

    try:
        # Step 1: Navigate to the Signup Page
        driver.get(f"{baseURL}/signup")
        print("Opened signup page.")

        # Step 2: Sign Up with New User Credentials
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("seleniumuser@example.com")
        password_input.send_keys("password123")
        password_input.send_keys(Keys.RETURN)
        print("Signed up with new user credentials.")

        # Step 3: Log In with the Same Credentials
        driver.get(baseURL)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys("seleniumuser@example.com")
        password_input.send_keys("password123")
        password_input.send_keys(Keys.RETURN)
        print("Logged in with the same credentials.")

        # Step 4: Verify Successful Login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_source = driver.page_source
        if "Book a Flight" in page_source: # title of the page
            print("Login successful, redirected to 'Book a Flight' page.")
        else:
            print("Login failed or redirection did not occur.")

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    test_user_signup_and_login()