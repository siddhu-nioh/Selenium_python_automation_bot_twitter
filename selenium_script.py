import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from PIL import Image
import traceback


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


CHROMEDRIVER_PATH = r"C:\\Windows\\chromedriver.exe"
service = Service(CHROMEDRIVER_PATH)
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")


USERNAME = "@bot1646026"
PASSWORD = "@HVNSking.123"
EMAIL_FOR_VERIFICATION = "siddhunioh7@gmail.com"  
TIMEOUT = 10  


processed_mentions = set()

def wait_for_element(driver, locator, timeout=TIMEOUT):
    """Wait for an element to be present and visible."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))

def wait_for_page_load(driver, timeout=TIMEOUT):
    """Wait until the page is fully loaded (no loading spinners)."""
    WebDriverWait(driver, timeout).until_not(
        EC.presence_of_element_located((By.XPATH, "//div[@role='progressbar']"))
    )

def login_to_twitter(driver, username, password):
    """Log in to Twitter with username and password."""
    try:
        driver.get("https://x.com/i/flow/login")
        wait_for_element(driver, (By.XPATH, "//input[@name='text']"))

        logging.info("Entering username.")
        username_field = driver.find_element(By.XPATH, "//input[@name='text']")
        username_field.send_keys(username)
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        try:
            logging.info("Checking for password field.")
            password_field = wait_for_element(driver, (By.XPATH, "//input[@name='password']"))
            password_field.send_keys(password)
        except TimeoutException:
            logging.warning("Password field not found. Entering email for verification.")
            email_field = wait_for_element(driver, (By.XPATH, "//input[@name='text']"))
            email_field.send_keys(EMAIL_FOR_VERIFICATION)
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
            password_field = wait_for_element(driver, (By.XPATH, "//input[@name='password']"))
            password_field.send_keys(password)

        driver.find_element(By.XPATH, "//span[text()='Log in']").click()
        logging.info("Login successful.")
    except Exception as e:
        logging.error(f"Failed to log in: {e}")
        raise

def crop_center_image(image_path, save_path):
    """Crop the image with only header profile like i take 23 percent from from left and 65 percent from right will be cropped ."""
    with Image.open(image_path) as img:
        width, height = img.size
        left = width * 0.23  
        top = height * 0.2   
        right = width * 0.65  
        bottom = height * 0.8
        cropped_image = img.crop((left, top, right, bottom))
        cropped_image.save(save_path)
    logging.info(f"Cropped screenshot saved as {save_path}.")


def capture_profile_screenshot(driver, username):
    """Capture a screenshot of the profile section and crop the center area."""
    try:
        wait_for_page_load(driver)  
        screenshot_path = os.path.abspath(f"{username}_full.png")
        driver.save_screenshot(screenshot_path)
        cropped_screenshot_path = os.path.abspath(f"{username}_profile.png")
        crop_center_image(screenshot_path, cropped_screenshot_path)
        os.remove(screenshot_path)
        return cropped_screenshot_path
    except Exception as e:
        logging.error(f"Failed to capture profile screenshot for {username}: {e}")
        raise
def click_reply_button(driver):
    """
    Locate and click the reply button for a specific mention.
    Handles obstructions and ensures the button is clicked properly.
    """
    try:
        logging.info("Attempting to locate and click the reply button.")

        
        reply_button = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='0 Replies. Reply' or contains(@aria-label, 'Reply')]"))
        )

        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply_button)
        time.sleep(0.5)  

        
        try:
            WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='0 Replies. Reply' or contains(@aria-label, 'Reply')]")))
            reply_button.click()
            logging.info("Reply button clicked successfully.")
        except Exception as e:

            logging.warning("Button not clickable via standard method. Using JavaScript to click.")
            driver.execute_script("arguments[0].click();", reply_button)
            logging.info("Reply button clicked using JavaScript.")
    except TimeoutException:
        logging.error("Reply button not found or not clickable.")
        raise RuntimeError("Reply button interaction failed due to obstruction or absence.")
def send_reply(driver):
    """
    Locate and click the final 'Reply' button to send the tweet.
    """
    try:
        logging.info("Attempting to locate and click the final Reply button.")

        
        reply_button = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Reply']"))
        )

        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply_button)
        time.sleep(0.5)

        
        try:
            WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Reply']")))
            reply_button.click()
            logging.info("Final Reply button clicked successfully.")
        except Exception as e:
            
            logging.warning("Final Reply button not clickable via standard method. Using JavaScript.")
            driver.execute_script("arguments[0].click();", reply_button)
            logging.info("Final Reply button clicked using JavaScript.")
    except TimeoutException:
        logging.error("Final Reply button not found or not clickable.")
        raise RuntimeError("Failed to send the reply due to interaction issues.")
def reply_to_mention(driver, username, screenshot_path):
    """Reply to a mention with the screenshot."""
    try:
        logging.info("Starting the reply process.")

        
        text_area = WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
        )
        text_area.send_keys(f"Hi @{username}, here's your profile screenshot!")
        logging.info("Message entered in the text area.")

        
        file_input = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        file_input.send_keys(screenshot_path)
        logging.info(f"Attached screenshot for @{username}.")
        
        
        time.sleep(5)

        
        send_reply(driver)
        logging.info("Send reply action triggered.")

        
        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'media-preview')]"))
            )
            logging.info("Media preview appeared successfully.")
        except TimeoutException:
            logging.warning("Media preview did not appear in the expected time. Continuing execution.")

        logging.info(f"Successfully replied to @{username} with the screenshot.")

    except Exception as e:
        logging.error(f"Failed to reply to @{username}: {e}")
        logging.debug(traceback.format_exc())
        raise

    finally:
        logging.info("Reply process finished.")




def process_mentions(driver):
    """Process a single Twitter mention by replying with a profile screenshot."""
    try:
        logging.info("Navigating to Mentions tab in Notifications.")
        notifications_button = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Notifications')]"))
        )
        notifications_button.click()

        mentions_tab = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/notifications/mentions')]"))
        )
        mentions_tab.click()

        logging.info("Finding mentions in Mentions tab.")

        mentions = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='User-Name']//a[@role='link']"))
        )

        for mention in mentions:
            try:
                href = mention.get_attribute("href")
                mentioned_username = href.split("/")[-1]  

                if mentioned_username in processed_mentions:
                    logging.info(f"Skipping already processed username: @{mentioned_username}")
                    continue

                processed_mentions.add(mentioned_username)

                logging.info(f"Navigating to profile of @{mentioned_username}.")
                mention.click()

                wait_for_page_load(driver)
                screenshot_path = capture_profile_screenshot(driver, mentioned_username)

                
                driver.back()
                wait_for_page_load(driver)

                
                click_reply_button(driver)

                
                reply_to_mention(driver, mentioned_username, screenshot_path)

                
                logging.info("Successfully replied to one mention. Stopping further processing.")
                return

            except Exception as e:
                logging.error(f"Error processing a mention: {e}")
                return

    except Exception as e:
        logging.error(f"General error occurred in process_mentions: {e}")
    finally:
        logging.info("Finished processing mentions.")

def main():
    driver = webdriver.Chrome(service=service, options=options)
    try:
        login_to_twitter(driver, USERNAME, PASSWORD)
        process_mentions(driver)
    finally:
        driver.quit()
        logging.info("Browser closed.")

if __name__ == "__main__":
    main()
