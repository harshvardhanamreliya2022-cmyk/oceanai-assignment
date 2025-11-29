"""
Selenium Test Script - Offline Version
Works without internet access by using manually installed ChromeDriver

Setup:
1. Download ChromeDriver manually from:
   https://chromedriver.chromium.org/downloads
   OR
   https://googlechromelabs.github.io/chrome-for-testing/

2. Extract and place chromedriver.exe in one of these locations:
   - C:\Windows\chromedriver.exe
   - C:\chromedriver\chromedriver.exe
   - Or any folder in your PATH
   - Or specify custom path in CHROMEDRIVER_PATH below

3. Run the script: python test_script.py
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
import time


# ==================== Configuration ====================

# IMPORTANT: Set this to your ChromeDriver path if not in PATH
CHROMEDRIVER_PATH = None  # e.g., r"C:\chromedriver\chromedriver.exe"

TEST_ID = "TC_DISCOUNT_CODE"
TEST_URL = "http://localhost:8080/simple_checkout.html"
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 10

# Get from environment
HEADLESS = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
VERBOSE = os.getenv('SELENIUM_VERBOSE', 'false').lower() == 'true'

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if VERBOSE else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Helper Functions ====================

def find_chromedriver():
    """Find ChromeDriver in common locations."""
    if CHROMEDRIVER_PATH and os.path.exists(CHROMEDRIVER_PATH):
        return CHROMEDRIVER_PATH

    # Common locations on Windows
    common_paths = [
        r"C:\Windows\chromedriver.exe",
        r"C:\chromedriver\chromedriver.exe",
        r"C:\Program Files\chromedriver\chromedriver.exe",
        r"C:\Program Files (x86)\chromedriver\chromedriver.exe",
        os.path.join(os.getcwd(), "chromedriver.exe"),
    ]

    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Found ChromeDriver at: {path}")
            return path

    # Try to use chromedriver from PATH
    import shutil
    chromedriver = shutil.which("chromedriver")
    if chromedriver:
        logger.info(f"Found ChromeDriver in PATH: {chromedriver}")
        return chromedriver

    return None


def setup_driver():
    """Initialize Chrome WebDriver (offline mode)."""
    logger.info("Setting up Chrome WebDriver (offline mode)...")

    # Chrome options
    options = Options()

    if HEADLESS:
        options.add_argument('--headless')
        logger.info("Running in headless mode")

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # Find ChromeDriver
    chromedriver_path = find_chromedriver()

    if not chromedriver_path:
        logger.error("❌ ChromeDriver not found!")
        logger.error("")
        logger.error("Please download ChromeDriver:")
        logger.error("1. Check your Chrome version: chrome://version")
        logger.error("2. Download matching ChromeDriver from:")
        logger.error("   https://chromedriver.chromium.org/downloads")
        logger.error("3. Extract and place in one of these locations:")
        logger.error("   - C:\\Windows\\chromedriver.exe")
        logger.error("   - C:\\chromedriver\\chromedriver.exe")
        logger.error("   - Or set CHROMEDRIVER_PATH in this script")
        logger.error("")
        raise FileNotFoundError("ChromeDriver not found")

    try:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(IMPLICIT_WAIT)
        logger.info("✅ WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"❌ Failed to initialize WebDriver: {e}")
        raise


def wait_for_element(driver, by, value, timeout=EXPLICIT_WAIT):
    """Wait for element to be present."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except Exception as e:
        logger.error(f"❌ Element not found: {by}={value}")
        raise


def wait_for_clickable(driver, by, value, timeout=EXPLICIT_WAIT):
    """Wait for element to be clickable."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except Exception as e:
        logger.error(f"❌ Element not clickable: {by}={value}")
        raise


# ==================== Test Case ====================

def test_discount_code():
    """Test applying SAVE15 discount code."""
    driver = None

    try:
        logger.info("=" * 60)
        logger.info(f"Starting Test: {TEST_ID}")
        logger.info("=" * 60)

        driver = setup_driver()

        # Navigate
        logger.info(f"Navigating to: {TEST_URL}")
        driver.get(TEST_URL)
        logger.info("✅ Page loaded")

        # Find discount field
        logger.info("Finding discount code field...")
        discount_field = wait_for_element(driver, By.ID, "discount-code")
        logger.info("✅ Discount field found")

        # Enter code
        logger.info("Entering discount code: SAVE15")
        discount_field.clear()
        discount_field.send_keys("SAVE15")
        logger.info("✅ Code entered")

        # Click apply
        logger.info("Clicking Apply button...")
        apply_button = wait_for_clickable(driver, By.ID, "apply-discount")
        apply_button.click()
        logger.info("✅ Apply clicked")

        # Wait for result
        time.sleep(1)

        # Verify discount
        logger.info("Verifying discount...")
        discount_amount = wait_for_element(driver, By.ID, "discount-amount")
        discount_text = discount_amount.text

        assert discount_text != "$0.00", "Discount was not applied"
        logger.info(f"✅ Discount applied: {discount_text}")

        # Verify total
        total_element = wait_for_element(driver, By.ID, "total")
        total_text = total_element.text
        logger.info(f"✅ Total: {total_text}")

        logger.info("=" * 60)
        logger.info("✅ TEST PASSED")
        logger.info("=" * 60)
        return True

    except AssertionError as e:
        logger.error(f"❌ Assertion failed: {e}")
        if driver:
            screenshot = f"error_{TEST_ID}_{int(time.time())}.png"
            driver.save_screenshot(screenshot)
            logger.error(f"Screenshot saved: {screenshot}")
        return False

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        if driver:
            screenshot = f"error_{TEST_ID}_{int(time.time())}.png"
            driver.save_screenshot(screenshot)
            logger.error(f"Screenshot saved: {screenshot}")
        return False

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


# ==================== Main ====================

if __name__ == "__main__":
    print("\nSelenium Test - Offline Mode")
    print("=" * 60)

    # Check if test server is running
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:8080", timeout=2)
        print("✅ Test server is running (http://localhost:8080)")
    except:
        print("⚠️  Test server not running!")
        print("\nStart the server in another terminal:")
        print("  cd test_data")
        print("  python -m http.server 8080")
        print("")
        sys.exit(1)

    print("")
    success = test_discount_code()
    sys.exit(0 if success else 1)
