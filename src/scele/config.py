"""Config-directory and credential-store locations (cross-platform)."""

import json
import os
import sys
from pathlib import Path

from . import BASE_URL


def _default_config_dir() -> Path:
    """Platform-appropriate config directory for the cookie store."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
        return Path(base) / "scele"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return (Path(xdg) if xdg else Path.home() / ".config") / "scele"


CONFIG_DIR = Path(os.environ["SCELE_CONFIG_DIR"]) if os.environ.get("SCELE_CONFIG_DIR") \
    else _default_config_dir()
COOKIES_PATH = CONFIG_DIR / "cookies.json"
WATCHES_DIR = CONFIG_DIR / "watches"


def base_url() -> str:
    """Return the SCELE base URL, overridable via SCELE_BASE_URL."""
    return os.environ.get("SCELE_BASE_URL", BASE_URL).rstrip("/")


def ensure_config_dir() -> Path:
    """Create the config directory if missing and return it."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def save_cookies(cookies: list[dict]) -> None:
    """Persist a list of {name, value, domain, path} cookie dicts."""
    ensure_config_dir()
    COOKIES_PATH.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
    try:
        COOKIES_PATH.chmod(0o600)
    except (OSError, NotImplementedError):
        pass


def load_cookies() -> list[dict]:
    """Load stored cookies, or return [] if none are saved."""
    if not COOKIES_PATH.exists():
        return []
    return json.loads(COOKIES_PATH.read_text(encoding="utf-8"))


def clear_cookies() -> None:
    """Delete the stored cookie file."""
    COOKIES_PATH.unlink(missing_ok=True)


def watches_dir() -> Path:
    """Return the directory holding background watch state, creating it if missing."""
    WATCHES_DIR.mkdir(parents=True, exist_ok=True)
    return WATCHES_DIR
