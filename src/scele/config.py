"""Config-directory and token-store locations (cross-platform)."""

import json
import os
import sys
import time
from pathlib import Path

from . import BASE_URL


def _default_config_dir() -> Path:
    """Platform-appropriate config directory for the token store."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
        return Path(base) / "scele"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return (Path(xdg) if xdg else Path.home() / ".config") / "scele"


CONFIG_DIR = Path(os.environ["SCELE_CONFIG_DIR"]) if os.environ.get("SCELE_CONFIG_DIR") \
    else _default_config_dir()
TOKEN_PATH = CONFIG_DIR / "token.json"
WATCHES_DIR = CONFIG_DIR / "watches"


def base_url() -> str:
    """Return the SCELE base URL, overridable via SCELE_BASE_URL."""
    return os.environ.get("SCELE_BASE_URL", BASE_URL).rstrip("/")


def ws_service() -> str:
    """Moodle web-service short name to mint tokens against (override for testing)."""
    return os.environ.get("SCELE_WS_SERVICE", "moodle_mobile_app")


def ensure_config_dir() -> Path:
    """Create the config directory if missing and return it."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def save_token(token: str, username: str = "", private_token: str = "") -> None:
    """Persist the minted web-service token (0600). The password is never stored."""
    ensure_config_dir()
    TOKEN_PATH.write_text(json.dumps({
        "token": token,
        "username": username,
        "private_token": private_token,
        "created_at": time.time(),
    }, indent=2), encoding="utf-8")
    try:
        TOKEN_PATH.chmod(0o600)
    except (OSError, NotImplementedError):
        pass


def load_token() -> dict | None:
    """Load the stored token dict, or None if there is no usable token."""
    if not TOKEN_PATH.exists():
        return None
    try:
        data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if data.get("token") else None


def clear_auth() -> None:
    """Delete the stored token file."""
    TOKEN_PATH.unlink(missing_ok=True)


def token_status() -> dict:
    """Masked overview for `scele whoami`; never exposes the raw token."""
    tok = load_token()
    if not tok:
        return {"stored": False}
    return {
        "stored": True,
        "username": tok.get("username") or None,
        "token_preview": (tok.get("token", "")[:6] + "…") if tok.get("token") else None,
        "age_days": round((time.time() - tok.get("created_at", 0)) / 86400, 1),
    }


def watches_dir() -> Path:
    """Return the directory holding background watch state, creating it if missing."""
    WATCHES_DIR.mkdir(parents=True, exist_ok=True)
    return WATCHES_DIR
