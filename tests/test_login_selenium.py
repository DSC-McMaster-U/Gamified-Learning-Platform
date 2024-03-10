"""
NOTE: These tests only work as of now when a flask local server is running in another terminal; I've
tried to find some way to automate opening up another subprocess running a flask server, but to no
avail (whether it be through the extremely-broken pytest-flask/multiprocessing libraries, or through using subprocess.Popen() 
to call a bash script that runs the flask server). 

For now, just open up another terminal in the root directory of the Gamified project, run 'flask --app ./app/run_app.py run', then
go back to your primary terminal and run pytest again.
"""

import pytest
from app.src.app import db, create_app
from time import sleep
# import subprocess

# selenium and webdriver-manager imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.errorhandler import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope='session')
def app():
    # set up a test flask application with a test client
    app = create_app(test_config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})

    # Set up: enter application context (necessary for database operations)
    with app.app_context():
        # create database tables
        db.create_all()
    
    yield app
    
    # Tear down: deletes all database tables created by the application during the test after testing is complete
    with app.app_context():
        db.session.remove()
        db.drop_all()
        
@pytest.fixture
def client(app):
    return app.test_client()  

# ...one of countless failed attempts using absolutely BS libraries to mitigate an absolutely BS issue; 
# keep for future reference in regards to running an automated flask server using subprocess library
# @pytest.fixture(scope="session")
# def client():
#     process = subprocess.Popen(['start /wait startServer.sh'], shell=True)
#     sleep(3)
#     yield

def test_login_html_btn_enabled(client):
    # Checks to see if the login submit button is enabled when all input fields are filled out
    
    # Set up selenium chrome webdriver options so that the testing browser is headless (invisible/no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize selenium's chrome driver and send it the login page
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                              options=chrome_options) # Also installs necessary up-to-date chrome drivers for selenium testing
    
    # NOTE: Comment the above and uncomment the below line to show the automated browser in action (for debugging):
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    try:
        driver.get(f"http://localhost:5000/login")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e

    # Locate and fill out the login input field forms
    emailInputField = driver.find_element(By.ID, "login-form-user")
    emailInputField.send_keys("TestUser")
    passInputField = driver.find_element(By.ID, "login-form-pwd")
    passInputField.send_keys("Test-12345")

    # Locate the form's submit button and check if the element is currently enabled
    submitBtn = driver.find_element(By.ID, "login-submit")
    assert submitBtn.is_enabled()

    # Close the chrome driver
    driver.close()

def test_login_html_btn_disabled(client):
    # Checks to see if the login submit button is disabled when not all input fields are filled out
    
    # Set up selenium chrome webdriver options so that the testing browser is headless (invisible/no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize selenium's chrome driver and send it the login page
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                            options=chrome_options) # Also installs necessary up-to-date chrome drivers for selenium testing
    
    try:
        driver.get(f"http://localhost:5000/login")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e

    # Locate the form's submit button and check if the element is currently disabled
    submitBtn = driver.find_element(By.ID, "login-submit")
    assert not submitBtn.is_enabled()

    # Close the chrome driver
    driver.close()

def test_login_html_email_error(client):
    # Checks to see if the flashed email error messages are actually being rendered to the login page

    # Set up selenium chrome webdriver options so that the testing browser is headless (invisible/no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize selenium's chrome driver and send it the login page
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                              options=chrome_options) # Also installs necessary up-to-date chrome drivers for selenium testing
    
    # NOTE: Comment the above and uncomment the below line to show the automated browser in action (for debugging):
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    try:
        driver.get(f"http://localhost:5000/login")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e

    # 1. Check if email error messages are displaying
    # Locate and fill out the login input field forms
    emailInputField = driver.find_element(By.ID, "login-form-user")
    emailInputField.send_keys("wrongemail@example.com")
    passInputField = driver.find_element(By.ID, "login-form-pwd")
    passInputField.send_keys("testPassword-123")

    # Locate the form's submit button and check if the element is currently enabled
    submitBtn = driver.find_element(By.ID, "login-submit")
    submitBtn.click()
    sleep(0.5)

    emailInputErr = driver.find_element(By.ID, "err-email")
    print(f"Email error: {emailInputErr.text}")
    assert emailInputErr.text == "A user with this email does not exist!"

    driver.close()

def test_login_html_pass_errors(client):   
    # Checks to see if the flashed password error messages are actually being rendered to the login page

    # Set up selenium chrome webdriver options so that the testing browser is headless (invisible/no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize selenium's chrome driver and send it the login page
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                              options=chrome_options) # Also installs necessary up-to-date chrome drivers for selenium testing
    
    # NOTE: Comment the above and uncomment the below line to show the automated browser in action (for debugging):
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    try:
        driver.get(f"http://localhost:5000/register")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e

    # Register an arbitrary account for testing using selenium
    # Locate register page form input field elements
    regNameInput = driver.find_element(By.ID, "form-name")
    regUserNameInput = driver.find_element(By.ID, "form-username")
    regDoBInput = driver.find_element(By.ID, "form-dob")
    regGradeInput = driver.find_element(By.ID, "form-grade")
    regEmailInput = driver.find_element(By.ID, "form-email")
    regConfEmailInput = driver.find_element(By.ID, "form-confirm-email")
    regPassInput = driver.find_element(By.ID, "form-pwd")
    regConfPassInput = driver.find_element(By.ID, "form-confirm-pwd")

    # Fill out input fields with info, then find and click on register submit button
    regNameInput.send_keys("John Smith")
    regUserNameInput.send_keys("johnsmith235")
    regDoBInput.click()
    regDoBInput.send_keys("20231001")
    regGradeInput.click()
    driver.find_element(By.XPATH, "//option[@value='SOPHOMORE']").click()
    regEmailInput.send_keys("johnsmith235@example.com")
    regConfEmailInput.send_keys("johnsmith235@example.com")
    regPassInput.send_keys("testPassword-123")
    regConfPassInput.send_keys("testPassword-123")

    regSubmitBtn = driver.find_element(By.ID, "register-submit")
    regSubmitBtn.click()
    sleep(0.5)

    # Login using the above account's email, but using an incorrect password
    try:
        driver.get(f"http://localhost:5000/login")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e
    
    # Locate and fill out the login input field forms
    emailInputField = driver.find_element(By.ID, "login-form-user")
    emailInputField.send_keys("johnsmith235@example.com")
    passInputField = driver.find_element(By.ID, "login-form-pwd")
    passInputField.send_keys("testPassword-12")

    # Locate the form's submit button and check if the element is currently enabled
    submitBtn = driver.find_element(By.ID, "login-submit")
    submitBtn.click()
    sleep(0.5)

    passInputErr = driver.find_element(By.ID, "err-pass")
    print(f"Email error: {passInputErr.text}")
    assert passInputErr.text == "Incorrect password. Try again or click Forgot password to reset it."    

    driver.close()

def test_login_html_locked_errors(client):
    # Checks to see if the flashed "locked-out" error messages are actually being rendered to the login page

    # Set up selenium chrome webdriver options so that the testing browser is headless (invisible/no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize selenium's chrome driver and send it the login page
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                              options=chrome_options) # Also installs necessary up-to-date chrome drivers for selenium testing
    
    # NOTE: Comment the above and uncomment the below line to show the automated browser in action (for debugging):
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    try:
        driver.get(f"http://localhost:5000/register")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e

    # Register an arbitrary account for testing using selenium
    # Locate register page form input field elements
    regNameInput = driver.find_element(By.ID, "form-name")
    regUserNameInput = driver.find_element(By.ID, "form-username")
    regDoBInput = driver.find_element(By.ID, "form-dob")
    regGradeInput = driver.find_element(By.ID, "form-grade")
    regEmailInput = driver.find_element(By.ID, "form-email")
    regConfEmailInput = driver.find_element(By.ID, "form-confirm-email")
    regPassInput = driver.find_element(By.ID, "form-pwd")
    regConfPassInput = driver.find_element(By.ID, "form-confirm-pwd")

    # Fill out input fields with info, then find and click on register submit button
    regNameInput.send_keys("John Smith")
    regUserNameInput.send_keys("johnsmith234")
    regDoBInput.click()
    regDoBInput.send_keys("20231001")
    regGradeInput.click()
    driver.find_element(By.XPATH, "//option[@value='SOPHOMORE']").click()
    regEmailInput.send_keys("johnsmith234@example.com")
    regConfEmailInput.send_keys("johnsmith234@example.com")
    regPassInput.send_keys("testPassword-123")
    regConfPassInput.send_keys("testPassword-123")

    regSubmitBtn = driver.find_element(By.ID, "register-submit")
    regSubmitBtn.click()
    sleep(0.5)

    # Login using the above account's email, but using an incorrect password multiple times
    try:
        driver.get(f"http://localhost:5000/login")
    except WebDriverException as e:
        message = """
        As of now, this test module requires running a flask server in the background (due to issues automating the opening the server 
        as a subprocess or live server)... first try running 'flask --app ./app/run_app.py run' in a separate terminal within the root
        dir, then attempt running 'pytest' again.
        """
        raise WebDriverException(message) from e
    
    # Locate and fill out the login input field form multiple times until locked out error message is triggered
    for _ in range(7):
        emailInputField = driver.find_element(By.ID, "login-form-user")
        emailInputField.clear()
        emailInputField.send_keys("johnsmith234@example.com")
        passInputField = driver.find_element(By.ID, "login-form-pwd")
        passInputField.send_keys("wrongPass")

        # Locate the form's submit button and check if the element is currently enabled
        submitBtn = driver.find_element(By.ID, "login-submit")
        submitBtn.click()
        sleep(0.5)

    # Check password error div and see if locked message is displaying, instead of standard "incorrect password" message
    passInputErr = driver.find_element(By.ID, "err-pass")
    assert passInputErr.text == "This account is locked. Please contact support to unlock your account and reset your password."    

    # Close the chrome driver
    driver.close()