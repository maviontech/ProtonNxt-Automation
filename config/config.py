import os
import json
from pathlib import Path


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


def _load_login_testdata():
    project_root = Path(__file__).resolve().parent.parent
    data_file = project_root / "testdata" / "login_data.json"
    if not data_file.exists():
        return {}

    with data_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_candidate_testdata():
    project_root = Path(__file__).resolve().parent.parent
    data_file = project_root / "testdata" / "candidate_data.json"
    if not data_file.exists():
        return {}

    with data_file.open("r", encoding="utf-8") as file:
        return json.load(file)


class Config:
    LOGIN_TESTDATA = _load_login_testdata()
    VALID_LOGIN = LOGIN_TESTDATA.get("valid_login", {})
    INVALID_LOGIN = LOGIN_TESTDATA.get("invalid_login", {})
    CANDIDATE_TESTDATA = _load_candidate_testdata()
    CANDIDATE_MANAGEMENT = CANDIDATE_TESTDATA.get("candidate_management", {})

    BASE_URL = os.getenv("PROTONNXT_URL", LOGIN_TESTDATA.get("base_url", "http://127.0.0.1:8000/"))
    BROWSER = os.getenv("PROTONNXT_BROWSER", "chrome").lower()

    COMPANY_CODE = os.getenv("PROTONNXT_COMPANY_CODE", VALID_LOGIN.get("company_code", ""))
    USERNAME = os.getenv("PROTONNXT_USERNAME", VALID_LOGIN.get("username", ""))
    PASSWORD = os.getenv("PROTONNXT_PASSWORD", VALID_LOGIN.get("password", ""))

    INVALID_COMPANY_CODE = os.getenv("PROTONNXT_INVALID_COMPANY_CODE", INVALID_LOGIN.get("company_code", "INVALID"))
    INVALID_USERNAME = os.getenv("PROTONNXT_INVALID_USERNAME", INVALID_LOGIN.get("username", "invalid@example.com"))
    INVALID_PASSWORD = os.getenv("PROTONNXT_INVALID_PASSWORD", INVALID_LOGIN.get("password", "invalid_password"))

    CHROME_BINARY = os.getenv("CHROME_BINARY", _default_chrome_binary())
    CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", _latest_cached_chromedriver())
