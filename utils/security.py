from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from typing import Any, Mapping


def _stringify_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return str(value)


def build_data_check_string(data: Mapping[str, Any]) -> str:
    prepared_parts = []
    for key in sorted(k for k in data.keys() if k != "hash" and data[k] is not None):
        prepared_parts.append(f"{key}={_stringify_value(data[key])}")
    return "\n".join(prepared_parts)


def verify_telegram_hash(payload: Mapping[str, Any], bot_token: str) -> bool:
    if "hash" not in payload:
        return False

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    data_check_string = build_data_check_string(payload)
    generated_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(generated_hash, str(payload["hash"]))


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def needs_reverification(last_verified: datetime | None, days: int) -> bool:
    if last_verified is None:
        return True
    delta = timedelta(days=days)
    return utcnow() - last_verified > delta


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
