"""Authenticated HTTP session wrapper around requests + BeautifulSoup."""

import re

import requests
from bs4 import BeautifulSoup

from . import __version__
from .config import base_url, load_cookies

USER_AGENT = f"scele-cli/{__version__} (+https://github.com/; python-requests)"
_SESSKEY_RE = re.compile(r'"sesskey":"([^"]+)"')


class NotAuthenticatedError(RuntimeError):
    """Raised when a request is redirected to the login page."""


class SceleSession:
    """Holds cookies + base URL and returns parsed pages."""

    def __init__(self, cookies: list[dict] | None = None):
        self.base = base_url()
        self.http = requests.Session()
        self.http.headers["User-Agent"] = USER_AGENT
        self._sesskey: str | None = None
        for c in cookies if cookies is not None else load_cookies():
            self.http.cookies.set(
                c["name"], c["value"],
                domain=c.get("domain", "").lstrip("."),
                path=c.get("path", "/"),
            )

    def url(self, path: str) -> str:
        """Resolve a path or absolute URL against the base URL."""
        if path.startswith("http"):
            return path
        return f"{self.base}/{path.lstrip('/')}"

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        """GET a page, raising NotAuthenticatedError on a login redirect."""
        resp = self.http.get(self.url(path), params=params, allow_redirects=True, timeout=30)
        resp.raise_for_status()
        if "/login/index.php" in resp.url and "login/index.php" not in self.url(path):
            raise NotAuthenticatedError("session expired or not logged in; run `scele login`")
        return resp

    def post(self, path: str, data: dict, params: dict | None = None) -> requests.Response:
        """POST form data and return the response."""
        resp = self.http.post(self.url(path), data=data, params=params, timeout=30)
        resp.raise_for_status()
        return resp

    def soup(self, path: str, params: dict | None = None) -> BeautifulSoup:
        """GET a page and parse it into a BeautifulSoup tree."""
        return BeautifulSoup(self.get(path, params).text, "lxml")

    def sesskey(self) -> str:
        """Return this session's sesskey token, fetching the dashboard once if needed."""
        if self._sesskey is None:
            resp = self.get("/my/")
            m = _SESSKEY_RE.search(resp.text)
            if not m:
                raise NotAuthenticatedError("could not read sesskey; run `scele login`")
            self._sesskey = m.group(1)
        return self._sesskey

    def is_authenticated(self) -> bool:
        """Return True if the stored session is currently valid."""
        try:
            self.get("/my/")
            return True
        except (NotAuthenticatedError, requests.HTTPError):
            return False
