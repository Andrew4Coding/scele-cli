"""Terminal login that captures the Moodle session cookie.

Prompts for username/password and POSTs them to Moodle's native login form
(SCELE has no CAPTCHA). Credentials are read from the terminal (password hidden)
or from SCELE_USERNAME / SCELE_PASSWORD for automation; they are sent once to
SCELE over HTTPS and never written to disk.
"""

import os
import sys
from getpass import getpass

import requests
from bs4 import BeautifulSoup

from . import __version__
from .config import base_url, save_cookies
from .output import fail

USER_AGENT = f"scele-cli/{__version__} (+https://github.com/; python-requests)"


def _say(msg: str = "") -> None:
    print(msg, file=sys.stderr)


def _prompt(label: str, secret: bool = False) -> str:
    if not sys.stdin.isatty():
        return sys.stdin.readline().strip()
    return (getpass(label) if secret else input(label)).strip()


def terminal_login(username: str | None = None, password: str | None = None) -> int:
    """Log in via the native Moodle username/password form, no browser."""
    base = base_url()
    http = requests.Session()
    http.headers["User-Agent"] = USER_AGENT

    try:
        page = http.get(f"{base}/login/index.php", timeout=30)
        page.raise_for_status()
    except requests.RequestException as e:
        fail(f"could not reach {base}: {e}", code="request_failed")

    token_el = BeautifulSoup(page.text, "lxml").select_one("input[name=logintoken]")
    logintoken = token_el.get("value", "") if token_el else ""

    username = username or os.environ.get("SCELE_USERNAME") or _prompt("SCELE username: ")
    password = password or os.environ.get("SCELE_PASSWORD") or _prompt("SCELE password: ", secret=True)
    if not username or not password:
        fail("username and password are required", code="request_failed")

    http.post(
        f"{base}/login/index.php",
        data={"anchor": "", "logintoken": logintoken,
              "username": username, "password": password},
        allow_redirects=True, timeout=30,
    )

    check = http.get(f"{base}/my/", allow_redirects=True, timeout=30)
    cookies = [
        {"name": c.name, "value": c.value, "domain": c.domain, "path": c.path}
        for c in http.cookies
    ]
    session_ok = any(c["name"].lower().startswith("moodlesession") for c in cookies)
    if "/login/index.php" in check.url or not session_ok:
        fail("login failed: check your username and password", code="login_failed")

    save_cookies(cookies)
    _say(f"Logged in as {username}. Saved session.")
    return 0
