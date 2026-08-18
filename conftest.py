from pathlib import Path
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config.config import Config


SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="Run browser headless")


@pytest.fixture(scope="session")
def base_url():
    return Config.BASE_URL


@pytest.fixture(scope="session")
def credentials():
    missing = []
    if not Config.COMPANY_CODE:
        missing.append("PROTONNXT_COMPANY_CODE")
    if not Config.USERNAME:
        missing.append("PROTONNXT_USERNAME")
    if not Config.PASSWORD:
        missing.append("PROTONNXT_PASSWORD")

    if missing:
        pytest.skip(f"Missing required environment variables for login smoke tests: {', '.join(missing)}")

    return {
        "company_code": Config.COMPANY_CODE,
        "username": Config.USERNAME,
        "password": Config.PASSWORD,
    }


@pytest.fixture(scope="session")
def invalid_credentials():
    return {
        "company_code": Config.INVALID_COMPANY_CODE,
        "username": Config.INVALID_USERNAME,
        "password": Config.INVALID_PASSWORD,
    }


@pytest.fixture(scope="session")
def candidate_testdata():
    return Config.CANDIDATE_MANAGEMENT


@pytest.fixture
def driver(request):
    options = Options()
    if Config.CHROME_BINARY:
        options.binary_location = Config.CHROME_BINARY
    if request.config.getoption("--headless"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if Config.BROWSER != "chrome":
        raise ValueError(f"Unsupported browser configured: {Config.BROWSER}")

    if Config.CHROMEDRIVER_PATH:
        service = Service(executable_path=Config.CHROMEDRIVER_PATH)
        browser = webdriver.Chrome(service=service, options=options)
    else:
        browser = webdriver.Chrome(options=options)

    browser.get(Config.BASE_URL)
    yield browser
    browser.quit()


@pytest.fixture(autouse=True)
def _store_test_context(request, credentials, invalid_credentials, candidate_testdata, base_url):
    request.node.test_context = {
        "base_url": base_url,
        "valid_credentials": {
            "company_code": credentials["company_code"],
            "username": credentials["username"],
            "password": "********",
        },
        "invalid_credentials": {
            "company_code": invalid_credentials["company_code"],
            "username": invalid_credentials["username"],
            "password": "********",
        },
        "candidate_testdata_available": bool(candidate_testdata),
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = item.nodeid.replace("::", "__").replace("/", "_").replace("\\", "_")
    screenshot_path = SCREENSHOT_DIR / f"{safe_name}_{timestamp}.png"

    driver.save_screenshot(str(screenshot_path))
    print(f"\nScreenshot captured: {screenshot_path}")
