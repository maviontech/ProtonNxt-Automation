import base64
from datetime import datetime
from pathlib import Path
import re

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config.config import Config


def _extract_case_id(nodeid):
    name = nodeid.split("::")[-1]
    match = re.search(r"test_([a-z]+(?:_[a-z]+)*)_(\d{3})_", name)
    if not match:
        return ""
    return f"{match.group(1).upper().replace('_', '-')}-{match.group(2)}"


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="Run browser headless")


@pytest.fixture(scope="session")
def base_url():
    return Config.BASE_URL


@pytest.fixture(scope="session")
def execution_started_at():
    return datetime.now()


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
        pytest.fail(f"Missing required login values: {', '.join(missing)}")

    return {
        "company_code": Config.COMPANY_CODE,
        "username": Config.USERNAME,
        "password": Config.PASSWORD,
    }


def _safe_credentials():
    if not (Config.COMPANY_CODE and Config.USERNAME and Config.PASSWORD):
        return None

    return {
        "company_code": Config.COMPANY_CODE,
        "username": Config.USERNAME,
        "password": Config.PASSWORD,
    }


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
    options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.notifications": 2,
        },
    )

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
def _store_test_context(
    request,
    base_url,
    execution_started_at,
):
    started_at = datetime.now()
    safe_credentials = _safe_credentials()
    request.node.test_context = {
        "base_url": base_url,
        "session_started_at": execution_started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "test_started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "valid_credentials": (
            {
                "company_code": safe_credentials["company_code"],
                "username": safe_credentials["username"],
                "password": "********",
            }
            if safe_credentials
            else "not provided"
        ),
    }


@pytest.fixture(autouse=True)
def _print_test_execution_details(request, base_url):
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Test Start] {request.node.nodeid}")
    print(f"[URL Under Test] {base_url}")
    print(f"[Execution Time] {started_at}")
    yield
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Test End] {request.node.nodeid}")
    print(f"[Completed At] {finished_at}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture the browser state after each test case and attach it to pytest-html when available."""
    outcome = yield
    report = outcome.get_result()

    # Keep reports focused on actionable evidence: capture only failed tests.
    if report.when != "call" or not report.failed:
        return

    browser = item.funcargs.get("driver")
    if browser is None:
        return

    screenshot_dir = Path(__file__).resolve().parent / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    test_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid).strip("_")
    case_id = _extract_case_id(item.nodeid)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_label = "failed"
    screenshot_prefix = f"{case_id}_{test_name}" if case_id else test_name
    screenshot_path = screenshot_dir / f"{screenshot_prefix}_{result_label}_{timestamp}.png"

    try:
        browser.save_screenshot(str(screenshot_path))
        if case_id:
            print(f"[Screenshot] [{case_id}] {screenshot_path}")
        else:
            print(f"[Screenshot] {screenshot_path}")

        pytest_html = item.config.pluginmanager.getplugin("html")
        if pytest_html is not None:
            extras = getattr(report, "extras", [])
            image_bytes = screenshot_path.read_bytes()
            extras.append(
                pytest_html.extras.png(
                    base64.b64encode(image_bytes).decode("utf-8"),
                    name=f"{result_label.title()} Screenshot",
                )
            )
            report.extras = extras
    except Exception as error:
        print(f"[Screenshot] Could not capture browser state: {error}")
