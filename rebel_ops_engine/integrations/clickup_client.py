import logging

import requests

from integrations.config import get

logger = logging.getLogger(__name__)

BASE_URL = "https://api.clickup.com/api/v2"

REBEL_OWNER_FIELD_ID = "cae19d32-798c-4a1d-8297-a8316df17ac4"
TEAM_FIELD_ID = "22e784ed-3abb-4af6-b960-6b6bb4e49f62"


def _headers():
    token = get("CLICKUP_API_TOKEN")
    if not token or token == "your_clickup_api_token_here":
        return None
    return {"Authorization": token, "Content-Type": "application/json"}


def create_task(title: str, description: str = "", priority: str = "medium", assignees: list[str] = None, owner: str = "", team: str = "", content: str = "") -> dict:
    headers = _headers()
    if not headers:
        logger.info("[CLICKUP MOCK] create_task(%s)", title)
        return {"status": "mocked", "title": title}

    list_id = get("CLICKUP_LIST_ID")
    if not list_id:
        logger.warning("[CLICKUP] No CLICKUP_LIST_ID set")
        return {"status": "error", "error": "No list ID configured"}

    priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    full_description = content[:5000] if content else (description[:2000] if description else "")
    body = {
        "name": title[:250],
        "description": full_description,
        "priority": priority_map.get(priority, 2),
        "custom_fields": [],
    }
    if owner:
        body["custom_fields"].append({"id": REBEL_OWNER_FIELD_ID, "value": owner})
    if team:
        body["custom_fields"].append({"id": TEAM_FIELD_ID, "value": team})
    if assignees:
        body["assignees"] = assignees

    try:
        resp = _request_with_retry("POST", f"{BASE_URL}/list/{list_id}/task", headers=headers, json=body, timeout=15)
        data = resp.json()
        logger.info("[CLICKUP] Created task: %s — id=%s", title, data.get("id"))
        return {"status": "created", "id": data.get("id"), "url": data.get("url")}
    except requests.RequestException as e:
        logger.error("[CLICKUP] Failed to create task: %s", e)
        return {"status": "error", "error": str(e)}


def get_tasks(status: str = "open") -> list[dict]:
    headers = _headers()
    if not headers:
        return []

    list_id = get("CLICKUP_LIST_ID")
    if not list_id:
        return []

    try:
        resp = _request_with_retry(
            "GET",
            f"{BASE_URL}/list/{list_id}/task",
            headers=headers,
            params={"include_closed": "false" if status == "open" else "true", "page": 0, "order_by": "updated"},
            timeout=15,
        )
        data = resp.json()
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "status": t.get("status", {}).get("status", ""),
                "priority": t.get("priority", {}).get("priority", ""),
                "assignees": [u["username"] for u in t.get("assignees", [])],
                "url": t.get("url"),
                "updated": t.get("date_updated"),
            }
            for t in data.get("tasks", [])
        ]
    except requests.RequestException as e:
        logger.error("[CLICKUP] Failed to list tasks: %s", e)
        return []


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    for attempt in range(3):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.RequestException:
            if attempt < 2:
                import time
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("Unreachable")


def clear_list():
    headers = _headers()
    if not headers:
        logger.info("[CLICKUP MOCK] clear_list()")
        return

    list_id = get("CLICKUP_LIST_ID")
    if not list_id:
        return

    try:
        resp = _request_with_retry(
            "GET",
            f"{BASE_URL}/list/{list_id}/task",
            headers=headers,
            params={"include_closed": "true", "page": 0, "order_by": "updated", "archived": "false"},
            timeout=15,
        )
    except requests.RequestException as e:
        logger.error("[CLICKUP] Failed to list tasks during clear: %s", e)
        return

    tasks = resp.json().get("tasks", [])
    if not tasks:
        return

    deleted = 0
    for t in tasks:
        task_id = t["id"]
        try:
            _request_with_retry("DELETE", f"{BASE_URL}/task/{task_id}", headers=headers, timeout=15)
            deleted += 1
        except requests.RequestException as e:
            logger.warning("[CLICKUP] Failed to delete task %s: %s", task_id, e)

    if deleted:
        logger.info("[CLICKUP] Cleared %d tasks from list %s", deleted, list_id)
