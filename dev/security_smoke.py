"""Destructive regression checks for an isolated instance with synthetic CI users only."""

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE = sys.argv[1].rstrip("/")
ADMIN_PASSWORD = "ci-only-not-production"
READER_PASSWORD = "ci-reader-not-production"


def check(label, condition):
    if not condition:
        raise AssertionError(label)
    print("PASS", label, flush=True)


def request(method, path, data=None, token=None, content_type=None):
    body = data
    if isinstance(data, dict):
        body = json.dumps(data).encode("utf-8")
        content_type = "application/json"
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    if token:
        headers["Cookie"] = "statping_auth=" + token
    req = Request(BASE + path, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=10) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def json_response(method, path, data=None, token=None, content_type=None):
    status, body = request(method, path, data, token, content_type)
    try:
        parsed = json.loads(body)
    except ValueError:
        parsed = None
    return status, parsed


for attempt in range(90):
    try:
        health_status, health = json_response("GET", "/health")
        if health_status == 200 and health and health.get("online") is True:
            break
    except (URLError, ConnectionError, TimeoutError):
        pass
    time.sleep(1)
else:
    raise AssertionError("Temporary Statping container did not become healthy")

check("health endpoint", health_status == 200 and health["online"] is True)
status, home = request("GET", "/")
check("public page loads", status == 200 and b"<html" in home.lower())

status, anonymous_core = json_response("GET", "/api")
check("public API stays available", status == 200 and isinstance(anonymous_core, dict))
check("public API omits admin secret", "api_secret" not in anonymous_core)

status, anonymous_users = json_response("GET", "/api/users")
check("anonymous user list denied", status == 401)

status, admin_login = json_response(
    "POST", "/api/login", urlencode({"username": "ciadmin", "password": ADMIN_PASSWORD}).encode(),
    content_type="application/x-www-form-urlencoded",
)
check("administrator login", status == 200 and admin_login and admin_login.get("admin") is True and admin_login.get("token"))
admin_token = admin_login["token"]

status, admin_claim = json_response(
    "POST", "/api/users/token", urlencode({"token": admin_token}).encode(),
    content_type="application/x-www-form-urlencoded",
)
check("administrator session validation", status == 200 and admin_claim and admin_claim.get("admin") is True)

status, initial_users = json_response("GET", "/api/users", token=admin_token)
check("administrator user list available", status == 200 and isinstance(initial_users, list) and len(initial_users) >= 1)
check("user list omits password hashes", all("password" not in user for user in initial_users))
admin_user = next((user for user in initial_users if user.get("username") == "ciadmin"), None)
check("administrator API key remains available", bool(admin_user and admin_user.get("api_key")))
admin_key = admin_user["api_key"]

status, created = json_response("POST", "/api/users", {
    "username": "security_reader",
    "email": "reader@example.invalid",
    "password": READER_PASSWORD,
    "admin": False,
}, token=admin_token)
check("administrator can create regular user", status == 200 and created and created.get("status") == "success")

status, users = json_response("GET", "/api/users", token=admin_token)
reader = next((user for user in users if user.get("username") == "security_reader"), None)
check("regular user has API key", status == 200 and reader and reader.get("admin") is False and bool(reader.get("api_key")))
check("user list still omits password hashes", all("password" not in user for user in users))
reader_key = reader["api_key"]

status, reader_login = json_response(
    "POST", "/api/login", urlencode({"username": "security_reader", "password": READER_PASSWORD}).encode(),
    content_type="application/x-www-form-urlencoded",
)
check("regular user login", status == 200 and reader_login and reader_login.get("admin") is False and reader_login.get("token"))
reader_token = reader_login["token"]

status, reader_claim = json_response(
    "POST", "/api/users/token", urlencode({"token": reader_token}).encode(),
    content_type="application/x-www-form-urlencoded",
)
check("regular user session validation", status == 200 and reader_claim and reader_claim.get("admin") is False)

status, _ = json_response("GET", "/api/users", token=reader_token)
check("regular user session cannot list users", status == 401)
status, _ = json_response("GET", "/api/users?" + urlencode({"api": reader_key}))
check("regular user API key cannot list users", status == 401)
status, _ = json_response("GET", "/api/users?api=invalid-key")
check("invalid API key cannot list users", status == 401)

status, reader_core = json_response("GET", "/api?" + urlencode({"api": reader_key}))
check("regular user API key retains read access", status == 200 and isinstance(reader_core, dict))
check("regular user API key cannot reveal admin secret", "api_secret" not in reader_core)

status, admin_core = json_response("GET", "/api?" + urlencode({"api": admin_key}))
check("administrator API key retains admin scope", status == 200 and admin_core and bool(admin_core.get("api_secret")))
status, _ = json_response("GET", "/api/users?" + urlencode({"api": admin_key}))
check("administrator API key can list users", status == 200)
status, _ = json_response("GET", "/api/users?" + urlencode({"api": admin_core["api_secret"]}))
check("global administrator secret retains admin scope", status == 200)

status, _ = json_response("POST", "/api/users?" + urlencode({"api": reader_key}), {
    "username": "illicit_admin",
    "email": "blocked@example.invalid",
    "password": "ci-blocked-not-production",
    "admin": True,
})
check("CVE admin creation attempt denied", status == 401)
status, users_after = json_response("GET", "/api/users", token=admin_token)
check("CVE attempt did not create an administrator", status == 200 and not any(user.get("username") == "illicit_admin" for user in users_after))

status, created = json_response("POST", "/api/services", {
    "name": "CI loopback health", "domain": "http://127.0.0.1:8080/health",
    "type": "http", "method": "GET", "expected_status": 200,
    "check_interval": 2, "timeout": 5, "public": True,
    "allow_notifications": False,
}, token=admin_token)
check("administrator can create a monitor", status == 200 and created and created.get("status") == "success")
successes = set()
for attempt in range(45):
    status, monitors = json_response("GET", "/api/services", token=admin_token)
    if status != 200 or not isinstance(monitors, list):
        raise AssertionError("monitor list unavailable")
    monitor = next((s for s in monitors if s.get("name") == "CI loopback health"), None)
    if monitor and monitor.get("online") and monitor.get("last_success"):
        successes.add(monitor["last_success"])
    if len(successes) >= 2:
        break
    time.sleep(1)
check("HTTP monitoring completes two successful scheduled checks", len(successes) >= 2)

print("All focused HTTP security and compatibility checks passed.", flush=True)
