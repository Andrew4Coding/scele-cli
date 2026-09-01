"""JSON rendering. Every command prints exactly one JSON document to stdout."""

import json as _json
import sys


def _plain(obj):
    if isinstance(obj, list):
        return [_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    return obj.to_dict() if hasattr(obj, "to_dict") else obj


def emit(obj, compact: bool = False) -> None:
    """Serialize obj (dataclass, list, or dict) as one JSON document."""
    _json.dump(
        _plain(obj), sys.stdout,
        ensure_ascii=False,
        separators=(",", ":") if compact else (",", ": "),
        indent=None if compact else 2,
    )
    sys.stdout.write("\n")


def fail(message: str, code: str = "error") -> None:
    """Print a JSON error document to stderr and exit non-zero."""
    _json.dump({"ok": False, "error": code, "message": message}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    raise SystemExit(1)
