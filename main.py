from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from audioToText import audio_to_text
import time
import requests
import os
import logging


def url_to_text(url: str):
    res = requests.get(url)
    with open(os.path.join(os.path.dirname(__file__), 'temp.mp3'), 'wb') as f:
        f.write(res.content)
    temp_text = audio_to_text(os.path.join(os.path.dirname(__file__), 'temp.mp3'))
    os.remove(os.path.join(os.path.dirname(__file__), 'temp.mp3'))
    return temp_text


chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', "enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
s = Service(ChromeDriverManager(log_level=logging.FATAL).install(), service_args=['--disable-logging'])
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
driver.get("https://myvisit.com/#!/home/signin/")
try:
    # Find reCAPTCHA iframe:
    iframe = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH,
                                                                               "//body[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/iframe[1]")))
    driver.switch_to.frame(iframe)
    # Click on reCAPTCHA tick box::
    element = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[1]/div/div/span/div[1]")))
    element.click()
except Exception as e:
    print(e)
    exit(1)
time.sleep(2)
# Check if recaptcha is ok
element = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[1]/div/div/span")
if element.get_attribute("aria-checked") != "true":
    # Need verification:"
    try:
        driver.switch_to.default_content()
        # Find reCAPTCHA challenge iframe:
        iframe = driver.find_element(By.XPATH, "/html/body/div[2]/div[4]/iframe")
        driver.switch_to.frame(iframe)
        # Click on reCAPTCHA voice verification button::
        element = driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/button")
        element.click()
        time.sleep(1)
        # finding the audio link:
        element = driver.find_element(By.XPATH, "/html/body/div/div/div[7]/a")
        link = element.get_attribute("href")
        # Transcribing the audio to text:
        text = url_to_text(link)
        element = driver.find_element(By.XPATH, "/html/body/div/div/div[6]/input")
        element.send_keys(text)
        time.sleep(1)
        # Click on reCAPTCHA submit button::
        element = driver.find_element(By.XPATH, "/html/body/div/div/div[8]/div[2]/div[1]/div[2]/button")
        element.click()
    except Exception as e:
        print(e)
        exit(1)

driver.switch_to.default_content()
# press on Continue without account
element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH,
                                                                            "//body[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/a[1]")))
element.click()
# press on Yes, continue anyway
element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH,
                                                                            "//body[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]/div[3]/button[1]")))
element.click()
# getting the session token
token = None
while token is None:
    time.sleep(0.5)
    token = driver.execute_script("return sessionStorage['user.session-token'];")
print(token)
driver.close()
