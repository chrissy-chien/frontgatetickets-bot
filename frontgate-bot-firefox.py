from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from solve_recaptcha import solve_recaptcha_audio
from selenium.webdriver.common.action_chains import ActionChains
import json

# for discord notifications
import requests
from datetime import datetime
bot_identifier = None
DISCORD_WEBHOOK_URL = "credentials.get(WEBHOOK_URL)"
DISCORD_MESSAGE = "Tickets Reserved Successfully via Firefox!"

def send_discord_notification(DISCORD_MESSAGE):
    data = {"content": DISCORD_MESSAGE}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print(f"Failed to send notification: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending notification: {e}")

def main():
    # Load credentials from passwords.json
    with open('passwords.json', 'r') as f:
        credentials = json.load(f)

    email = credentials.get("EMAIL")
    password = credentials.get("PASSWORD")
    card_number = credentials.get("CARD_NUMBER")
    expiration = credentials.get("EXPIRATION")
    cvv = credentials.get("CVV")

    ###########################
    desired_qty = 5  # Number of tickets to purchase - 1
    options = FirefoxOptions()
    #options.add_argument("--headless")  # Run in headless mode if desired
    max_wait_time = 3600  # Maximum wait time in seconds (1 hour)
    ###########################

    #options = webdriver.FirefoxOptions()
    #options.add_argument("--headless=new")
    #options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_argument("--window-size=1920,1080")
    #options.add_argument("--disable-infobars")
    #options.add_argument("--start-maximized")
    #options.add_argument("--no-sandbox")
    #options.add_argument("--disable-dev-shm-usage")

    driver = Firefox(options=options)  # or webdriver.Firefox(options=options) for Firefox

    print("Navigating to event page...")
    driver.get("https://nitehartsfestival.frontgatetickets.com/event/j8l47xv1mru9qyz8/")
    #driver.get("https://lostindreams.frontgatetickets.com/event/5ogdnhrefopntv2o/")

    # In the queue, wait for the "Add to Cart" button to appear (wait up to 1 hour)
    wait = WebDriverWait(driver, max_wait_time)
    try:
        print("Waiting in queue...")
        #add_to_cart_button = wait.until(EC.presence_of_element_located((By.ID, "btn-add-cart")))
        ticket_descriptionm = wait.until(EC.presence_of_element_located((By.ID, "eventContentInfo")))
    except:
        driver.quit()
        exit()

    print("Ticket description found, proceeding to refresh until able to buy tickets...")
    while True:
        try:
            add_to_cart_button = driver.find_element(By.ID, "btn-add-cart")
            if add_to_cart_button.is_displayed():
                print("Add to Cart button found, proceeding with ticket selection...")
                break
        except:
            print("Add to Cart button not found, refreshing...")
            driver.refresh()
            time.sleep(2)  # wait before trying again

    qty_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sel-qty")))
    inc_button = driver.find_element(By.CLASS_NAME, "fbtn-quantity-up")

    print("Increasing ticket quantity...")
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

    print("Clicking Add to Cart button...")
    add_to_cart_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-add-cart")))
    add_to_cart_button.click()
    print("Add to Cart clicked, waiting for loading modal to disappear...")
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-modal")))


    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal-dialog")))

    print("Checking for Captcha popup...")
    try:
        captcha_popup = driver.find_element(By.ID, "modal-captcha")
        print("Attempting to solve Captcha...")

        solve_recaptcha_audio(driver, wait)

        print("Captcha solved, proceeding with submit button...")
        submit_button = wait.until(EC.element_to_be_clickable((By.ID, "div-btn-modal-submit")))
        submit_button.click()
    except:
        pass

    try:
        print("Closing popup...")
        close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-link")))
        close_button.click()

        print("Checking for cart button...")
        cart_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "cart-icon")))
        cart_button.click()
    except:
        pass

    send_discord_notification(DISCORD_MESSAGE)
    '''try:
        print("Checking for checkout button...")
        #success_screen = driver.find_element(By.ID, "cart-success-header")
        checkout_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-cart-success")))
        print("Checkout button found, clicking...")
        checkout_button.click()
    except:
        pass

    print("Sending Discord notification...")
    send_discord_notification(DISCORD_MESSAGE)

    try:
        print("Attempting to sign in...")
        navbar_signin_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#link-global-signin")))
        navbar_signin_button.click()

        email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#txt-login-email")))
        #actions = ActionChains(driver)
        #actions.move_to_element(email_field).click().perform()
        #time.sleep(0.1)
        email_field.send_keys(email)

        password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#txt-login-pass")))
        password_field.send_keys(password)

        signin_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-user-signin")))
        signin_button.click()
    except:
        pass

    try:
        print("In checkout, filling in shipping details...")
        shipping_button = wait.until(EC.presence_of_element_located((By.ID, "btn-shipping-submit")))
        shipping_button.click()

        print("Entering payment details...")
        card_button = wait.until(EC.element_to_be_clickable((By.ID, "creditCardPmButton")))
        card_button.click()
        print("Success!")
    except:
        pass'''

    time.sleep(2000)

    driver.quit()

if __name__ == "__main__":
    main()