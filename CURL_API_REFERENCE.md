# DavnorShield API: complete cURL reference

This reference covers every HTTP route currently registered by the application.
It assumes the API is running on `http://localhost:8000` and uses the default
`/api/v1` prefix. Change `BASE_URL` if yours differs.

## Setup

```bash
export BASE_URL="http://localhost:8000"
export API="$BASE_URL/api/v1"
export TOKEN="paste-access-token-here"
export AUTH="Authorization: Bearer $TOKEN"

# Replace these with records returned by the reference endpoints.
export MUNICIPALITY_ID="00000000-0000-0000-0000-000000000001"
export BARANGAY_ID="00000000-0000-0000-0000-000000000002"
export USER_ID="00000000-0000-0000-0000-000000000003"
export REPORT_ID="00000000-0000-0000-0000-000000000004"
export SCHOOL_ID="00000000-0000-0000-0000-000000000005"
export THREAT_PATTERN_ID="00000000-0000-0000-0000-000000000006"
```

`$TOKEN` is the `token.access_token` returned by login or registration. JSON
requests include `Content-Type: application/json`; file submission uses
`multipart/form-data` and must not set that header manually.

Roles are `citizen`, `barangay_admin`, `municipality_admin`, `school_admin`,
and `super_admin`. A super admin satisfies a municipality- or school-admin
role requirement. “Admin” below means any administrative role.

## Service routes

### `GET /` — service identity and status

```bash
curl -sS "$BASE_URL/"
```

Returns the application name, version, and `ok` status. No authentication.

### `GET /health` — liveness check

```bash
curl -sS "$BASE_URL/health"
```

Returns `{ "status": "healthy" }`. No authentication.

## Authentication

### `POST /api/v1/auth/register` — create an account

```bash
curl -sS -X POST "$API/auth/register" \
  -H 'Content-Type: application/json' \
  -d '{
    "full_name": "Jane Citizen",
    "email": "jane@example.com",
    "password": "change-this-password",
    "phone": "+639171234567",
    "role": "citizen",
    "municipality_id": null,
    "barangay_id": null,
    "is_active": true
  }'
```

Creates a user and returns the public user object plus a bearer token. `full_name`,
`email`, and an 8–128 character `password` are required. `role` defaults to
`citizen`, and locality IDs may be `null`.

### `POST /api/v1/auth/login` — obtain a bearer token

```bash
curl -sS -X POST "$API/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"jane@example.com","password":"change-this-password"}'
```

Authenticates a user and returns `token.access_token`, `token.token_type`, and
`token.expires_in`. Set `TOKEN` to the returned access token before calling a
protected route.

### `GET /api/v1/auth/me` — current active user

```bash
curl -sS "$API/auth/me" -H "$AUTH"
```

Returns the authenticated active user’s full profile.

### `PUT /api/v1/auth/change-password` — change own password

```bash
curl -sS -X PUT "$API/auth/change-password" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"current_password":"change-this-password","new_password":"new-secure-password"}'
```

Changes the active caller’s password. Both password values must be at least
eight characters.

### `DELETE /api/v1/auth/deactivate-account` — deactivate own account

```bash
curl -sS -X DELETE "$API/auth/deactivate-account" -H "$AUTH"
```

Deactivates the caller’s account. An inactive account cannot use active-user
routes afterward.

## Users (admin only)

### `GET /api/v1/users/` — list users

```bash
curl -sS "$API/users/?page=1&size=20&search=jane&role=citizen&is_active=true" -H "$AUTH"
```

Returns a paginated user list. `page` defaults to 1; `size` defaults to 20 and
must be 1–100. `search`, `role`, and `is_active` are optional filters.

### `GET /api/v1/users/{user_id}` — retrieve one user

```bash
curl -sS "$API/users/$USER_ID" -H "$AUTH"
```

Returns one user by UUID.

### `PUT /api/v1/users/{user_id}` — update a user

```bash
curl -sS -X PUT "$API/users/$USER_ID" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"full_name":"Jane Updated","role":"citizen","is_active":true}'
```

Updates any supplied fields. Valid fields are `full_name`, `email`, `phone`,
`password`, `role`, `municipality_id`, `barangay_id`, and `is_active`.

### `DELETE /api/v1/users/{user_id}` — delete a user

```bash
curl -sS -X DELETE "$API/users/$USER_ID" -H "$AUTH"
```

Permanently deletes the specified user.

### `GET /api/v1/users/barangay/{barangay_id}` — users in a barangay

```bash
curl -sS "$API/users/barangay/$BARANGAY_ID?page=1&size=20" -H "$AUTH"
```

Returns paginated users assigned to a barangay.

### `GET /api/v1/users/municipality/{municipality_id}` — users in a municipality

```bash
curl -sS "$API/users/municipality/$MUNICIPALITY_ID?page=1&size=20" -H "$AUTH"
```

Returns paginated users assigned to a municipality.

## Scam reports

### `POST /api/v1/reports/` — submit a report (active user)

```bash
curl -sS -X POST "$API/reports/" -H "$AUTH" \
  -F 'report_type=phishing' \
  -F 'title=Fake bank sign-in page' \
  -F 'description=The link requested my banking credentials.' \
  -F "municipality_id=$MUNICIPALITY_ID" \
  -F "barangay_id=$BARANGAY_ID" \
  -F 'suspicious_url=https://example.test/login' \
  -F 'phone_number=+639171234567' \
  -F 'qr_data=https://example.test/login' \
  -F 'screenshot=@/absolute/path/to/screenshot.png;type=image/png'
```

Submits a report as multipart form data. Required fields are `report_type`,
`title`, `description`, `municipality_id`, and `barangay_id`. `suspicious_url`,
`phone_number`, `qr_data`, and `screenshot` are optional; omit any that do not
apply. `screenshot` must point to a real local file.

### `GET /api/v1/reports/` — list reports

```bash
curl -sS "$API/reports/?page=1&size=20&category=phishing&status=pending&municipality=$MUNICIPALITY_ID&barangay=$BARANGAY_ID&start_date=2026-09-01&end_date=2026-09-05"
```

Returns paginated reports. Every query filter is optional: `category` is one
of `phishing`, `sms_scam`, `qr_scam`, `marketplace_scam`, `fake_job`,
`fake_investment`, `identity_theft`, `malware`, or `other`; `status` is
`pending`, `verified`, `resolved`, or `rejected`. `date=YYYY-MM-DD` is a
single-day shortcut when no start/end dates are supplied. This list endpoint
does not currently require authentication.

### `GET /api/v1/reports/{report_id}` — retrieve one report

```bash
curl -sS "$API/reports/$REPORT_ID"
```

Returns a report by UUID. No authentication is currently enforced.

### `PATCH /api/v1/reports/{report_id}/status` — change a report status

```bash
curl -sS -X PATCH "$API/reports/$REPORT_ID/status" \
  -H 'Content-Type: application/json' \
  -d '{"status":"verified"}'
```

Sets the status to `pending`, `verified`, `resolved`, or `rejected`. No
authentication is currently enforced by this route.

### `DELETE /api/v1/reports/{report_id}` — delete a report

```bash
curl -sS -X DELETE "$API/reports/$REPORT_ID"
```

Permanently deletes the report. No authentication is currently enforced.

### `GET /api/v1/reports/barangay/{barangay_id}` — barangay report feed

```bash
curl -sS "$API/reports/barangay/$BARANGAY_ID?page=1&size=20"
```

Returns paginated reports for one barangay. No authentication is currently enforced.

### `GET /api/v1/reports/municipality/{municipality_id}` — municipality report feed

```bash
curl -sS "$API/reports/municipality/$MUNICIPALITY_ID?page=1&size=20"
```

Returns paginated reports for one municipality. No authentication is currently enforced.

## Scanners

### `POST /api/v1/scanner/url` — scan a URL

```bash
curl -sS -X POST "$API/scanner/url" \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.test/login"}'
```

Analyzes a valid absolute URL and returns risk score, level, category,
explanation, and recommendations. No authentication.

### `POST /api/v1/scanner/sms` — scan an SMS

```bash
curl -sS -X POST "$API/scanner/sms" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Your account is locked. Verify now at https://example.test"}'
```

Analyzes a non-empty SMS message. No authentication.

### `POST /api/v1/scanner/qr` — scan QR content

```bash
curl -sS -X POST "$API/scanner/qr" \
  -H 'Content-Type: application/json' \
  -d '{"qr_data":"https://example.test/pay"}'
```

Analyzes non-empty decoded QR content, not an image file. No authentication.

### `POST /api/v1/scanner/text` — scan free-form text

```bash
curl -sS -X POST "$API/scanner/text" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Send your OTP to claim the prize."}'
```

Analyzes the `text` member of the JSON object. No authentication.

## Alerts

### `GET /api/v1/alerts/today` — today’s alerts

```bash
curl -sS "$API/alerts/today"
```

Returns all alerts created today. No authentication.

### `GET /api/v1/alerts/active` — active alerts

```bash
curl -sS "$API/alerts/active?page=1&size=20"
```

Returns paginated active alerts. No authentication.

### `GET /api/v1/alerts/barangay/{barangay_id}` — barangay alerts

```bash
curl -sS "$API/alerts/barangay/$BARANGAY_ID?page=1&size=20"
```

Returns paginated alerts for a barangay. No authentication.

### `GET /api/v1/alerts/municipality/{municipality_id}` — municipality alerts

```bash
curl -sS "$API/alerts/municipality/$MUNICIPALITY_ID?page=1&size=20"
```

Returns paginated alerts for a municipality. No authentication.

### `POST /api/v1/alerts/broadcast` — broadcast an alert (municipality admin or super admin)

```bash
curl -sS -X POST "$API/alerts/broadcast" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{
    \"threat_pattern_id\": \"$THREAT_PATTERN_ID\",
    \"municipality_id\": \"$MUNICIPALITY_ID\",
    \"barangay_id\": \"$BARANGAY_ID\",
    \"alert_level\": \"high\",
    \"title\": \"Phishing campaign detected\",
    \"message\": \"Avoid links requesting your credentials.\"
  }"
```

Creates an alert. `threat_pattern_id`, `municipality_id`, `title`, and
`message` are required. `barangay_id` is optional, and `alert_level` defaults
to `medium` (`low`, `medium`, `high`, and `critical` are valid).

## Cyber weather

### `GET /api/v1/weather/today` — today’s municipality forecast

```bash
curl -sS "$API/weather/today?municipality_id=$MUNICIPALITY_ID"
```

Returns today’s weather record, or `null` if none exists. `municipality_id` is required.

### `GET /api/v1/weather/history` — municipality forecast history

```bash
curl -sS "$API/weather/history?municipality_id=$MUNICIPALITY_ID&page=1&size=20"
```

Returns weather history. `municipality_id` is required; `size` limits the
service query (1–100). The response reports page metadata, although the current
service only applies the size limit rather than an offset.

### `GET /api/v1/weather/municipality/{municipality_id}` — latest forecast

```bash
curl -sS "$API/weather/municipality/$MUNICIPALITY_ID"
```

Returns the latest weather record for the municipality, or `null`. No authentication.

## Heatmap

### `GET /api/v1/heatmap/municipality` — municipality heatmap

```bash
curl -sS "$API/heatmap/municipality"
```

Returns municipality-level heatmap items. No authentication.

### `GET /api/v1/heatmap/barangay` — barangay heatmap

```bash
curl -sS "$API/heatmap/barangay"
```

Returns barangay-level heatmap items. No authentication.

### `GET /api/v1/heatmap/statistics` — combined heatmap data

```bash
curl -sS "$API/heatmap/statistics"
```

Returns the combined heatmap statistics payload. No authentication.

## Reference locations

### `GET /api/v1/barangays/` — list barangays

```bash
curl -sS "$API/barangays/"
```

Returns all barangays with IDs and municipality IDs. No authentication.

### `GET /api/v1/barangays/{barangay_id}` — retrieve a barangay

```bash
curl -sS "$API/barangays/$BARANGAY_ID"
```

Returns one barangay by UUID. No authentication.

### `GET /api/v1/barangays/municipality/{municipality_id}` — barangays in a municipality

```bash
curl -sS "$API/barangays/municipality/$MUNICIPALITY_ID"
```

Returns all barangays in the municipality. No authentication.

### `GET /api/v1/municipalities/` — list municipalities

```bash
curl -sS "$API/municipalities/"
```

Returns all municipalities. No authentication.

### `GET /api/v1/municipalities/{municipality_id}` — retrieve a municipality

```bash
curl -sS "$API/municipalities/$MUNICIPALITY_ID"
```

Returns one municipality by UUID. No authentication.

### `GET /api/v1/municipalities/summary` — municipality statistics

```bash
curl -sS "$API/municipalities/summary"
```

Intended to return municipality summary statistics. **Current route order bug:**
the earlier `/{municipality_id}` route captures `summary`, which then fails UUID
validation with 422. Move `/summary` above `/{municipality_id}` in
`app/api/v1/municipalities.py` to make this cURL call succeed.

## Dashboard (municipality admin or super admin)

### `GET /api/v1/dashboard/lgu` — LGU dashboard

```bash
curl -sS "$API/dashboard/lgu" -H "$AUTH"
```

Returns the full LGU dashboard aggregate.

### `GET /api/v1/dashboard/admin` — administrative dashboard

```bash
curl -sS "$API/dashboard/admin" -H "$AUTH"
```

Returns the same dashboard aggregate through the administrative route.

### `GET /api/v1/dashboard/analytics` — analytics aggregate

```bash
curl -sS "$API/dashboard/analytics" -H "$AUTH"
```

Returns the dashboard analytics aggregate.

### `GET /api/v1/dashboard/top-threats` — top threat categories

```bash
curl -sS "$API/dashboard/top-threats" -H "$AUTH"
```

Returns the `top_threat_categories` section of the dashboard.

### `GET /api/v1/dashboard/outbreaks` — active outbreaks

```bash
curl -sS "$API/dashboard/outbreaks" -H "$AUTH"
```

Returns the `active_outbreaks` section of the dashboard.

## Schools (school admin or super admin)

### `GET /api/v1/schools/` — list schools

```bash
curl -sS "$API/schools/?page=1&size=20&municipality_id=$MUNICIPALITY_ID" -H "$AUTH"
```

Returns paginated school awareness records. `municipality_id` is optional.

### `GET /api/v1/schools/{school_id}` — retrieve a school

```bash
curl -sS "$API/schools/$SCHOOL_ID" -H "$AUTH"
```

Returns one school’s awareness and phishing statistics.

### `GET /api/v1/schools/stats` — school dashboard statistics

```bash
curl -sS "$API/schools/stats?municipality_id=$MUNICIPALITY_ID" -H "$AUTH"
```

Intended to return phishing and report statistics. **Current route order bug:**
the earlier `/{school_id}` route captures `stats` and returns a 422 UUID error.
Move `/stats` above `/{school_id}` in `app/api/v1/schools.py` to enable it.

### `PATCH /api/v1/schools/awareness-score` — set a school awareness score

```bash
curl -sS -X PATCH "$API/schools/awareness-score" \
  -H "$AUTH" -H 'Content-Type: application/json' \
  -d "{\"school_id\":\"$SCHOOL_ID\",\"awareness_score\":87.5}"
```

Updates the selected school’s awareness score. The score is required and must
be between 0 and 100 inclusive.

## Useful HTTP outcomes

- `200` successful read, update, scan, login, or delete; `201` successful registration, report submission, or alert broadcast.
- `401` missing, expired, or invalid bearer token; `403` inactive account or insufficient role.
- `404` record not found; `422` invalid UUID, malformed body, missing required field, or invalid query parameter.
- Add `-i` to any command to see response headers and status, or add `| jq` to pretty-print JSON when `jq` is installed.

## Chat & RAG API

These endpoints provide a lightweight AI chat interface backed by a RAG pipeline. They exist under the API v1 prefix (default: `/api/v1`). Replace `BASE_URL` and `TOKEN` with your deployment values.

### POST /api/v1/chat/

Start or continue a conversation and receive a model response with retrieved sources.

Request JSON:

{
  "conversation_id": "<optional-uuid>",
  "prompt": "How can I spot a phishing email?",
  "top_k": 5,
  "temperature": 0.0
}

Example curl:

curl -X POST "${BASE_URL:-http://localhost:8000}/api/v1/chat/" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"How can I spot a phishing email?","top_k":5}'

Example response (200):

{
  "conversation_id": "11111111-2222-3333-4444-555555555555",
  "message": "Common signs of phishing include unexpected links, misspelled domains, urgent action requests...",
  "sources": [
    {"id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","score":0.92,"snippet":"...from the official bank domain..."}
  ]
}

---

### GET /api/v1/chat/conversations/{conversation_id}/messages

List messages for a conversation (paginated by `limit`).

Example curl:

curl -X GET "${BASE_URL:-http://localhost:8000}/api/v1/chat/conversations/<conversation_id>/messages?limit=100" \
  -H "Authorization: Bearer ${TOKEN}"

Example response:

[
  {"id":"...","role":"user","content":"How do I...","metadata":null,"created_at":"..."},
  {"id":"...","role":"assistant","content":"...","metadata":null,"created_at":"..."}
]

---

### POST /api/v1/chat/documents/upload

Upload a document (text) to the RAG index. The server will chunk and index it (background tasks recommended).

Request JSON:

{
  "source": "manual-upload",
  "text": "Full document text here..."
}

Example curl:

curl -X POST "${BASE_URL:-http://localhost:8000}/api/v1/chat/documents/upload" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"source":"manual-upload","text":"This is a short doc to index."}'

Example response (201):

{
  "id": "22222222-3333-4444-5555-666666666666",
  "chunk_count": 1
}

---

Notes:
- The chat endpoint performs: embed(prompt) -> retrieve top_k docs -> assemble prompt (system + retrieved + history) -> call LLM -> return message + source snippets.
- Authentication and rate limits apply per existing API policies.
- The public JSON key `metadata` is preserved in API responses even though the internal SQLAlchemy model uses `meta_data` to avoid reserved-name conflicts.

