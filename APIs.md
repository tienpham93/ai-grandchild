# API Documentation 🔌

This document provides a comprehensive reference for the REST APIs, webhooks, and simulation endpoints exposed by the **AI Grandchild** backend server.

### Base URLs
* **Local Development:** `http://localhost:8000`
* **Secure Public Tunnel:** `https://ai-grandchild-vn.loca.lt`

---

## 🔑 Authentication API

### 1. Admin Login
Verifies administrator credentials against the SQLite database.

* **Endpoint:** `POST /api/login`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "admin_password_here"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Login successful"
  }
  ```
* **Error Responses:**
  * `400 Bad Request`: Missing username or password.
  * `401 Unauthorized`: Invalid username or password.

---

## 🏠 Family Directories API

### 1. List Families
Retrieves all registered families.

* **Endpoint:** `GET /api/families`
* **Success Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "name": "Gia đình Ngoại Bảy"
    }
  ]
  ```

### 2. Create Family
Registers a new unique family directory.

* **Endpoint:** `POST /api/families`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "name": "Gia đình Ngoại Bảy"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "id": 1,
    "name": "Gia đình Ngoại Bảy"
  }
  ```
* **Error Responses:**
  * `400 Bad Request`: Family name already exists or missing name parameter.

### 3. Delete Family
Deletes an entire family directory. Cascades deletions to all associated members and messages.

* **Endpoint:** `DELETE /api/families/{family_id}`
* **Success Response (200 OK):**
  ```json
  {
    "status": "deleted"
  }
  ```
* **Error Responses:**
  * `404 Not Found`: Family ID does not exist.

---

## 👥 Whitelisted Members API

### 1. List Whitelisted Members
Retrieves all authorized family members across all family directories.

* **Endpoint:** `GET /api/members`
* **Success Response (200 OK):**
  ```json
  [
    {
      "chat_id": "7799435300",
      "family_id": 1,
      "name": "Ngoại Bảy",
      "member_type": "senior",
      "member_role": "grandpa",
      "bank_account": "987654321"
    }
  ]
  ```

### 2. Authorize Member (Create)
Adds a new authorized member to a specific family directory.

* **Endpoint:** `POST /api/members`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "chat_id": "7799435300",
    "family_id": 1,
    "name": "Ngoại Bảy",
    "member_type": "senior",
    "member_role": "grandpa",
    "bank_account": "987654321"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "chat_id": "7799435300",
    "family_id": 1,
    "name": "Ngoại Bảy",
    "member_type": "senior",
    "member_role": "grandpa",
    "bank_account": "987654321"
  }
  ```
* **Error Responses:**
  * `400 Bad Request`: Database insertion failed or constraint violation (e.g., duplicate `chat_id`).

### 3. Update Member Profile
Updates role classifications, names, or bank account bindings.

* **Endpoint:** `PUT /api/members/{chat_id}`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "name": "Ngoại Bảy",
    "member_type": "senior",
    "member_role": "grandpa",
    "bank_account": "987654321"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "chat_id": "7799435300",
    "family_id": 1,
    "name": "Ngoại Bảy",
    "member_type": "senior",
    "member_role": "grandpa",
    "bank_account": "987654321"
  }
  ```
* **Error Responses:**
  * `404 Not Found`: Chat ID not found.

### 4. Revoke Member Access (Delete)
Deletes a member from the database, revoking their chat access.

* **Endpoint:** `DELETE /api/members/{chat_id}`
* **Success Response (200 OK):**
  ```json
  {
    "status": "deleted"
  }
  ```

---

## 🤖 Agent Configurations API

### 1. List Agents
Retrieves current behavioral settings and system prompts for all active agents.

* **Endpoint:** `GET /api/agents`
* **Success Response (200 OK):**
  ```json
  [
    {
      "id": "companion",
      "name": "Companion Agent",
      "goal": "Engage in warm, attentive, and protective grandchild conversations...",
      "system_prompt": "You are 'AI Grandchild', an extremely attentive, warm..."
    }
  ]
  ```

### 2. Update Agent Configuration
Rewrites an agent's goal description and underlying system prompt dynamically.

* **Endpoint:** `PUT /api/agents/{agent_id}`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "goal": "New updated agent goal description",
    "system_prompt": "New updated system instruction for Gemini API"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "id": "companion",
    "name": "Companion Agent",
    "goal": "New updated agent goal description",
    "system_prompt": "New updated system instruction for Gemini API"
  }
  ```

---

## ⏰ Automation Hub Rules API

### 1. List Automation Rules
Retrieves all configured automation jobs.

* **Endpoint:** `GET /api/automation`
* **Success Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "name": "Check-in Ngoại Bảy after 60m",
      "job_type": "inactivity_check",
      "family_id": 1,
      "target_chat_id": "7799435300",
      "interval_minutes": 60,
      "alert_family": true,
      "cron_time": null,
      "cron_day_of_week": null,
      "is_active": true,
      "last_run": "2026-06-30T15:30:00"
    }
  ]
  ```

### 2. Create Automation Rule
Registers a new background scheduled automation job.

* **Endpoint:** `POST /api/automation`
* **Content-Type:** `application/json`
* **Request Body (Inactivity Check):**
  ```json
  {
    "name": "Check-in Ngoại Bảy after 60m",
    "job_type": "inactivity_check",
    "family_id": 1,
    "target_chat_id": "7799435300",
    "interval_minutes": 60,
    "alert_family": true
  }
  ```
* **Request Body (Scheduled Family Digest):**
  ```json
  {
    "name": "Weekly Digest: Family ID 1",
    "job_type": "family_digest",
    "family_id": 1,
    "target_chat_id": "family",
    "cron_time": "18:00",
    "cron_day_of_week": "Friday"
  }
  ```
* **Success Response (200 OK):**
  * Returns the created `AutomationJob` JSON object.

### 3. Delete Automation Rule
Deletes an automation job, stopping the background scheduler thread from checking it.

* **Endpoint:** `DELETE /api/automation/{job_id}`
* **Success Response (200 OK):**
  ```json
  {
    "status": "deleted"
  }
  ```

---

## 🔌 Inbound Gateways & Webhooks

### 1. Telegram Inbound Webhook
Receives and processes updates dispatched from Telegram's webhook.

* **Endpoint:** `POST /telegram-webhook`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "update_id": 982103820,
    "message": {
      "message_id": 12,
      "from": {
        "id": 7799435300,
        "is_bot": false,
        "first_name": "Ngoại Bảy"
      },
      "chat": {
        "id": 7799435300,
        "type": "private"
      },
      "date": 1782617057,
      "text": "Hello grandchild"
    }
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "status": "success"
  }
  ```
* **Ignored Responses (Returns 200 OK to prevent Telegram retry flooding):**
  * `{"status": "ignored", "reason": "Unregistered Chat ID"}` (Access Control/Whitelist block)
  * `{"status": "ignored", "reason": "Empty or non-text message"}`

---

## 🧪 Postman Simulation Endpoints

### 1. Simulate Bank SMS Webhook
Simulates a transaction alert sent from an external bank API (such as HSBC). Relational mapping queries the owner of the `bank_account`, resolves their `chat_id`, and initiates the pipeline.

* **Endpoint:** `POST /test/bank_sms_webhook`
* **Content-Type:** `application/json`
* **Request Body:**
  ```json
  {
    "bank_app_id": "hsbc_vn",
    "bank_account": "987654321",
    "transaction_id": "TXN_9821038201",
    "sms_content": "Acct 987654321: -$5,000 at GLOBAL TRAVEL CORP at 14:30. Grandma's SSN: 123-45-6789."
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "message": "Simulated transaction for Ngoại Bảy (grandpa) resolved to chat_id 7799435300"
  }
  ```
* **Error Responses:**
  * `404 Not Found`: Bank account is not linked to any authorized member.

---

## 💻 Health & Static Routing

### 1. Root Health Check
Used for automated monitoring and webhook validation.

* **Endpoint:** `GET /`
* **Query Parameters:** `challenge` (Optional)
* **Success Response (200 OK - No Challenge):**
  ```json
  {
    "status": "running",
    "service": "AI Grandchild Webhook API"
  }
  ```
* **Success Response (200 OK - With Challenge):**
  * Returns the raw `challenge` string as `text/plain` payload.

### 2. Serve Static Verification Files
Serves files from the `/static` directory for domain-verification procedures.

* **Endpoint:** `GET /{filename}`
* **Success Response (200 OK):**
  * Returns the requested file payload.
* **Error Responses:**
  * `404 Not Found`: Requested file does not exist.
