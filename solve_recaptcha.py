import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydub import AudioSegment
import speech_recognition as sr
import undetected_chromedriver as uc

def solve_recaptcha_audio(driver, wait):
    driver.switch_to.default_content()

    # 1. Switch to reCAPTCHA iframe and click checkbox
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'recaptcha')]")))
    driver.switch_to.frame(iframe)
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
    checkbox.click()

    driver.switch_to.default_content()

    # 2. Switch to challenge iframe
    challenge_iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'challenge')]")))
    driver.switch_to.frame(challenge_iframe)

    # 3. Click audio challenge
    audio_button = wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-audio-button")))
    audio_button.click()

    # 4. Get audio download link
    audio_src = wait.until(EC.presence_of_element_located((By.ID, "audio-source"))).get_attribute("src")
    print(f"[INFO] Found audio src: {audio_src}")

    # 5. Download audio file
    audio_content = requests.get(audio_src, stream=True)
    with open("captcha.mp3", "wb") as f:
        for chunk in audio_content.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    # 6. Convert MP3 to WAV
    sound = AudioSegment.from_mp3("captcha.mp3")
    sound.export("captcha.wav", format="wav")

    # 7. Transcribe using Google STT
    recognizer = sr.Recognizer()
    with sr.AudioFile("captcha.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print(f"[INFO] Transcribed text: {text}")
        except:
            print("[ERROR] Could not transcribe audio.")
            text = ""

    # 8. Enter text and submit
    input_field = wait.until(EC.presence_of_element_located((By.ID, "audio-response")))
    input_field.send_keys(text)
    driver.find_element(By.ID, "recaptcha-verify-button").click()

    # Cleanup
    os.remove("captcha.mp3")
    os.remove("captcha.wav")

    driver.switch_to.default_content()
    print("[INFO] CAPTCHA attempt finished.")