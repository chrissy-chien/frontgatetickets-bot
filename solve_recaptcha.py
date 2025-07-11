import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydub import AudioSegment
import speech_recognition as sr

def solve_recaptcha_audio(driver, wait):
    driver.switch_to.default_content()

    # 1. Switch to reCAPTCHA iframe and click checkbox
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]")))
    driver.switch_to.frame(iframe)
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
    checkbox.click()

    time.sleep(1)

    is_checked = checkbox.get_attribute("aria-checked")
    if is_checked == "true":
        print("[INFO] CAPTCHA solved by checkbox, skipping audio challenge.")
        driver.switch_to.default_content()
        time.sleep(0.5)
        return  # exit the function as CAPTCHA is solved
    else:
        print("[INFO] Checkbox not sufficient, proceeding with audio challenge.")

    driver.switch_to.default_content()

    while True:
        try:
            # Switch to challenge iframe
            challenge_iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'challenge')]")))
            driver.switch_to.frame(challenge_iframe)

            # Click audio challenge
            audio_button = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-audio-button")))
            audio_button.click()

            # Download audio
            audio_src = wait.until(EC.presence_of_element_located((By.ID, "audio-source"))).get_attribute("src")
            print(f"[INFO] Found audio src: {audio_src}")

            audio_content = requests.get(audio_src, stream=True)
            with open("captcha.mp3", "wb") as f:
                for chunk in audio_content.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # Convert to WAV
            sound = AudioSegment.from_mp3("captcha.mp3")
            sound.export("captcha.wav", format="wav")

            # Transcribe
            recognizer = sr.Recognizer()
            with sr.AudioFile("captcha.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    print(f"[INFO] Transcribed text: {text}")
                except:
                    print("[ERROR] Could not transcribe audio.")
                    text = ""

            # Submit transcription
            input_field = wait.until(EC.presence_of_element_located((By.ID, "audio-response")))
            input_field.clear()
            input_field.send_keys(text)
            driver.find_element(By.ID, "recaptcha-verify-button").click()

            # Cleanup
            os.remove("captcha.mp3")
            os.remove("captcha.wav")

            # Check if error message is shown
            time.sleep(2)
            error_divs = driver.find_elements(By.CLASS_NAME, "rc-audiochallenge-error-message")
            if error_divs and any("Multiple correct solutions required" in e.text for e in error_divs):
                print("[INFO] Multiple correct solutions required. Retrying...")
                driver.switch_to.default_content()
                time.sleep(1)
                continue  # Loop again to re-download and retry

            print("[INFO] CAPTCHA attempt finished successfully.")
            driver.switch_to.default_content()
            break

        except TimeoutException:
            print("[ERROR] Timeout while solving audio CAPTCHA, retrying...")
            driver.switch_to.default_content()
            time.sleep(2)
            continue