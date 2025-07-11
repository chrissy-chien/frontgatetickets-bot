from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from RecaptchaBypass.RecaptchaSolver import RecaptchaSolver
from selenium.webdriver.chrome.options import Options

# for discord notifications
import requests
from datetime import datetime
bot_identifier = None
DISCORD_WEBHOOK_URL = "credentials.get(WEBHOOK_URL)"
DISCORD_MESSAGE = "Tickets Reserved Successfully!"

def send_discord_notification(DISCORD_MESSAGE):
    data = {"content": DISCORD_MESSAGE}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print(f"Failed to send notification: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

###########################
desired_qty = 5  # Number of tickets to purchase - 1
email = "your.email@gmail.com"
password = "password123"  # Replace with your actual password
options = Options()
#options.add_argument("--headless")  # Run in headless mode if desired
options.add_argument("--remote-debugging-port=5000")
options.add_argument("--user-data-dir=C:/Users/chien/AppData/Local/Temp/selenium_frontgate")  # Use a persistent user profile for cookies/session
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
max_wait_time = 3600  # Maximum wait time in seconds (1 hour)
###########################

#options = webdriver.FirefoxOptions()
#options.add_argument("--headless")  # Run in headless mode if desired
driver = webdriver.Chrome(options=options)  # or webdriver.Firefox(options=options) for Firefox

# driver.get("https://nitehartsfestival.frontgatetickets.com/event/j8l47xv1mru9qyz8/")
driver.get("https://lostindreams.frontgatetickets.com/event/5ogdnhrefopntv2o/")

# In the queue, wait for the "Add to Cart" button to appear (wait up to 1 hour)
wait = WebDriverWait(driver, max_wait_time)
try:
    add_to_cart_button = wait.until(EC.presence_of_element_located((By.ID, "btn-add-cart")))
except:
    driver.quit()
    exit()

qty_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sel-qty")))
inc_button = driver.find_element(By.CLASS_NAME, "fbtn-quantity-up")

while True:
    current_qty = int(qty_elem.get_attribute("value"))
    if current_qty >= desired_qty:
        break

    if not inc_button.is_enabled():
        break

    inc_button.click()
    time.sleep(0.2)  # slight delay to allow UI to update

    # re-read quantity to check if it changed
    new_qty = int(qty_elem.get_attribute("value"))
    if new_qty == current_qty:
        break

add_to_cart_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-add-cart")))
add_to_cart_button.click()
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-modal")))

recaptchaSolver = RecaptchaSolver(driver)

wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal-dialog")))

try:
    captcha_popup = driver.find_element(By.ID, "modal-captcha")
    recaptchaSolver.solveCaptcha()

    submit_button = wait.until(EC.element_to_be_clickable((By.ID, "div-btn-modal-submit")))
    submit_button.click()
except:
    pass

try:
    #success_screen = driver.find_element(By.ID, "cart-success-header")
    checkout_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-cart-success")))
    checkout_button.click()
except:
    pass

send_discord_notification(DISCORD_MESSAGE)

'''try:
    email_input = wait.until(EC.presence_of_element_located((By.ID, "txt-login-email")))
    driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
    email_input.click()
    time.sleep(0.1)
    email_input.clear()
    email_input.send_keys(email)

    wait.until(EC.element_to_be_clickable((By.ID, "txt-login-pass")))
    password_input = driver.find_element(By.ID, "txt-login-pass")
    password_input.click()
    password_input.clear()
    password_input.send_keys(password)

    signin_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-user-signin")))
    signin_button.click()
except:
    pass'''



time.sleep(200)

driver.quit()