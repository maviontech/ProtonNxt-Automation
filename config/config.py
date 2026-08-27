import os
import json
from pathlib import Path

from dotenv import load_dotenv


def _default_chrome_binary():
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return ""


def _latest_cached_chromedriver():
    root = Path.home() / ".cache" / "selenium" / "chromedriver" / "win64"
    if not root.exists():
        return ""

    version_dirs = [path for path in root.iterdir() if path.is_dir()]
    if not version_dirs:
        return ""

    def version_key(path):
        try:
            return tuple(int(part) for part in path.name.split("."))
        except ValueError:
            return (0,)

    latest_dir = sorted(version_dirs, key=version_key, reverse=True)[0]
    driver_path = latest_dir / "chromedriver.exe"
    return str(driver_path) if driver_path.exists() else ""


def _load_testdata(filename):
    project_root = Path(__file__).resolve().parent.parent
    data_file = project_root / "testdata" / filename
    if not data_file.exists():
        return {}

    with data_file.open("r", encoding="utf-8") as file:
        return json.load(file)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _env(name, default=""):
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


class Config:
    LOGIN_TESTDATA = _load_testdata("login_data.json")
    LOGIN_SMOKE_TESTDATA = _load_testdata("login_smoke_data.json")
    ADD_MEMBER_TESTDATA = _load_testdata("add_member_data.json")
    ADD_MEMBER_SMOKE_TESTDATA = _load_testdata("add_member_smoke_data.json")
    CREATE_CUSTOMER_SMOKE_TESTDATA = _load_testdata("create_customer_smoke_data.json")
    MANAGE_MEMBERS_TESTDATA = _load_testdata("manage_members_data.json")
    MANAGE_MEMBERS_SMOKE_TESTDATA = _load_testdata("manage_members_smoke_data.json")
    CREATE_TEAM_TESTDATA = _load_testdata("create_team_data.json")
    CREATE_TEAM_SMOKE_TESTDATA = _load_testdata("create_team_smoke_data.json")
    CREATE_JD_SMOKE_TESTDATA = _load_testdata("create_jd_smoke_data.json")
    VALID_LOGIN = LOGIN_TESTDATA.get("valid_login", {})
    LOCK_TEST_LOGIN = LOGIN_TESTDATA.get("lock_test_login", {})

    BASE_URL = _env("PROTONNXT_URL", LOGIN_TESTDATA.get("base_url", "http://127.0.0.1:8000/"))
    BROWSER = _env("PROTONNXT_BROWSER", "chrome").lower()

    COMPANY_CODE = _env("PROTONNXT_COMPANY_CODE", VALID_LOGIN.get("company_code", ""))
    USERNAME = _env("PROTONNXT_USERNAME", VALID_LOGIN.get("username", ""))
    PASSWORD = _env("PROTONNXT_PASSWORD", VALID_LOGIN.get("password", ""))
    RECRUITER_COMPANY_CODE = _env("PROTONNXT_RECRUITER_COMPANY_CODE", COMPANY_CODE)
    RECRUITER_USERNAME = _env("PROTONNXT_RECRUITER_USERNAME", "")
    RECRUITER_PASSWORD = _env("PROTONNXT_RECRUITER_PASSWORD", PASSWORD)
    INACTIVE_COMPANY_CODE = _env("PROTONNXT_INACTIVE_COMPANY_CODE", COMPANY_CODE)
    INACTIVE_USERNAME = _env("PROTONNXT_INACTIVE_USERNAME", "")
    INACTIVE_PASSWORD = _env("PROTONNXT_INACTIVE_PASSWORD", PASSWORD)
    BLOCKED_TENANT_COMPANY_CODE = _env("PROTONNXT_BLOCKED_TENANT_COMPANY_CODE", "")
    BLOCKED_TENANT_USERNAME = _env("PROTONNXT_BLOCKED_TENANT_USERNAME", "")
    BLOCKED_TENANT_PASSWORD = _env("PROTONNXT_BLOCKED_TENANT_PASSWORD", "")
    GRANDFATHERED_TENANT_COMPANY_CODE = _env("PROTONNXT_GRANDFATHERED_TENANT_COMPANY_CODE", "")
    GRANDFATHERED_TENANT_USERNAME = _env("PROTONNXT_GRANDFATHERED_TENANT_USERNAME", "")
    GRANDFATHERED_TENANT_PASSWORD = _env("PROTONNXT_GRANDFATHERED_TENANT_PASSWORD", "")

    LOCK_TEST_COMPANY_CODE = _env("PROTONNXT_LOCK_TEST_COMPANY_CODE", LOCK_TEST_LOGIN.get("company_code", COMPANY_CODE))
    LOCK_TEST_USERNAME = _env("PROTONNXT_LOCK_TEST_USERNAME", LOCK_TEST_LOGIN.get("username", USERNAME))
    LOCK_TEST_PASSWORD = _env("PROTONNXT_LOCK_TEST_PASSWORD", LOCK_TEST_LOGIN.get("password", PASSWORD))
    LOCK_TEST_WRONG_PASSWORD = _env(
        "PROTONNXT_LOCK_TEST_WRONG_PASSWORD",
        LOCK_TEST_LOGIN.get("wrong_password", "WrongPass@123"),
    )
    ACCOUNT_LOCK_TIMEOUT_SECONDS = float(_env("PROTONNXT_ACCOUNT_LOCK_TIMEOUT_SECONDS", "0"))
    ACCOUNT_LOCK_MAX_ATTEMPTS = int(_env("PROTONNXT_ACCOUNT_LOCK_MAX_ATTEMPTS", "5"))
    LOCK_MESSAGE_KEYWORDS = tuple(
        keyword.strip().lower()
        for keyword in _env(
            "PROTONNXT_LOCK_MESSAGE_KEYWORDS",
            "locked,lockout,too many attempts,temporarily disabled,try again later",
        ).split(",")
        if keyword.strip()
    )

    CHROME_BINARY = _env("CHROME_BINARY", _default_chrome_binary())
    CHROMEDRIVER_PATH = _env("CHROMEDRIVER_PATH", _latest_cached_chromedriver())
    LOGIN_TYPE_DELAY = float(_env("PROTONNXT_LOGIN_TYPE_DELAY", "0.05"))
    LOGIN_STEP_DELAY = float(_env("PROTONNXT_LOGIN_STEP_DELAY", "0.1"))
    SHOW_PASSWORD_WHILE_TYPING = _env("PROTONNXT_SHOW_PASSWORD_WHILE_TYPING", "true").lower() == "true"
    CREATE_JD_COMPANY = _env("PROTONNXT_CREATE_JD_COMPANY", "")
    CREATE_JD_COMPANY_SEARCH = _env("PROTONNXT_CREATE_JD_COMPANY_SEARCH", "a")
