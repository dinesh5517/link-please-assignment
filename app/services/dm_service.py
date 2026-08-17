import os
import requests
from typing import Dict, Any, Optional

PSEUDOGRAM_BASE_URL = os.getenv("PSEUDOGRAM_BASE_URL", "https://pseudogram-api.onrender.com")
# Load API key from environment; do NOT hardcode a default value here.
PSEUDOGRAM_API_KEY = os.getenv("PSEUDOGRAM_API_KEY", "")


class RateLimitError(Exception):
    def __init__(self, retry_after: int = 60, message: str = "Rate limited"):
        self.retry_after = retry_after
        self.message = message
        super().__init__(self.message)


class TemporaryAPIError(Exception):
    pass


class FatalAPIError(Exception):
    pass


def send_dm(
    recipient_user_id: str,
    message: str,
    comment_id: str,
    idempotency_key: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends a DM request to PseudoGram API.
    Returns payload dict containing dm_id and status on success (202).
    Raises RateLimitError on 429, TemporaryAPIError on 500, FatalAPIError on 400.
    """
    key = api_key or PSEUDOGRAM_API_KEY
    url = f"{PSEUDOGRAM_BASE_URL}/v1/dm/send"

    headers = {
        "X-API-Key": key,
        "Content-Type": "application/json"
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    payload = {
        "recipient_user_id": recipient_user_id,
        "message": message,
        "comment_id": comment_id
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise TemporaryAPIError(f"Network error when calling DM API: {str(e)}")

    if response.status_code in (200, 202):
        return response.json()

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        retry_sec = int(retry_after) if retry_after and retry_after.isdigit() else 60
        raise RateLimitError(retry_after=retry_sec, message="429 Rate limited by PseudoGram API")

    if response.status_code == 500:
        raise TemporaryAPIError("500 Internal error from PseudoGram API")

    if response.status_code == 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise FatalAPIError(f"400 Invalid Request: {detail}")

    raise TemporaryAPIError(f"Unexpected status code {response.status_code}: {response.text}")


def get_dm_status(dm_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Queries the status of a DM from PseudoGram API.
    Does NOT count against rate limits.
    """
    key = api_key or PSEUDOGRAM_API_KEY
    url = f"{PSEUDOGRAM_BASE_URL}/v1/dm/{dm_id}"

    headers = {
        "X-API-Key": key
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise TemporaryAPIError(f"Network error checking DM status: {str(e)}")

    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        raise FatalAPIError(f"DM {dm_id} not found")

    raise TemporaryAPIError(f"Unexpected status code {response.status_code} when checking status: {response.text}")
