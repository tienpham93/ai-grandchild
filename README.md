
# AI Grandchild 🛡️

**AI Grandchild** is an intelligent, multi-agent proactive companion designed to protect elderly relatives from predatory, high-pressure vacation club and timeshare scams (such as high-pressure presentation traps and fraudulent bank draft schemes). 

Acting as a warm digital grandchild, the system intercepts incoming communications on Telegram, performs real-time privacy scrubbing and security risk analysis, engages the senior in protective dialogue, and dispatches automated security alerts to configured family guardians.

---

## 🏗️ System Architecture & Workflow

The system is designed as a decoupled architecture utilizing a local relational **SQLite** database, **FastAPI** for background task execution, and **Streamlit** for administrative operations.

```text
[ Telegram User Message ]
           │
           ▼
   [ FastAPI Gateway ] 
           │
           ├──► (Whitelisting check against SQLite database)
           │
           ▼ (Queued to Background Task)
   [ 🛡️ Anonymizer Skill ] ──► (Regex PII scrubbing: SSNs, bank card formats)
           │
           ▼ (Anonymized Payload)
   [ 🔍 Investigator Agent ] ──► (Generative risk analysis & reasoning)
           │
           ├── [ If Risk is LOW/MEDIUM/HIGH ]
           │   ▼
           │   [ 💬 Companion Agent ] ──► (Warm, context-aware grandchild dialogue)
           │                                 │
           │                                 ▼
           │                     [ Sends reply to Senior on Telegram ]
           │
           └── [ If Risk is HIGH ]
               ▼
               [ 🚨 Bridge Agent ] ──► (Drafts urgent family alert)
                                             │
                                             ▼
                                 [ Sends alert to Family on Telegram ]
```

### Active Agents & Skills
1. **🛡️ Anonymizer Skill (`src/skills/anonymizer.py`):** Intercepts raw inputs and automatically scrubs sensitive PII (Social Security Numbers, national identity cards, and bank account digits) using regex patterns *before* any prompt hits the LLM.
2. **🔍 Investigator Agent (`src/agents/investigator.py`):** Synthesizes incoming messages with dynamic geofencing context and behavioral search results to assess security risks (`LOW`, `MEDIUM`, or `HIGH`).
3. **💬 Companion Agent (`src/agents/companion.py`):** Acts as the digital grandchild. Converses in warm, respectful English, dynamically adapting its protective tone depending on the risk level identified by the Investigator.
4. **🚨 Bridge Agent (`src/agents/bridge.py`):** Formulates concise, urgent, and actionable security notifications to be dispatched immediately to all registered family guardians on Telegram when a `HIGH` risk is detected.

---

## 🔑 Prerequisites & Preparations

Before launching, you must obtain a Gemini API Key, set up a Telegram Bot, and capture the unique chat IDs for your test accounts.

### 1. Obtain a Google Gemini API Key
1. Navigate to [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google account.
3. Click **Get API Key** and generate a new key.
4. Save this key; you will add it as `GEMINI_API_KEY` in your `.env` file.

### 2. Create a Telegram Bot
1. Open the Telegram app and search for the official account **`@BotFather`**.
2. Start a chat and send the command:
   ```text
   /newbot
   ```
3. Follow the instructions to give your bot a Display Name (e.g., `AI Grandchild`) and a unique Username ending in `_bot` (e.g., `ai_grandchild_en_bot`).
4. `@BotFather` will generate an **HTTP API Token** (e.g., `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`). Copy this token and save it as `TELEGRAM_BOT_TOKEN` in your `.env` file.

### 3. Capture Telegram Chat IDs (Senior & Family Accounts)
You need to identify the unique Telegram ID for both the Senior account (Grandpa) and the Family Member account. **Note: A Telegram Chat ID is not a phone number.**

1. On Telegram, search for **`@userinfobot`**.
2. Start a chat with the bot. It will instantly reply with your profile's unique **`Id`** (a 9-to-10-digit number).
3. Do this for both accounts. You will use these IDs to register and authorize your users in the Admin Dashboard.

---

## ⚙️ Environment Configuration

Create a file named `.env` in your project root directory and populate it with your keys:

```env
GEMINI_API_KEY="your_actual_gemini_api_key"
TELEGRAM_BOT_TOKEN="your_actual_bot_token"
```

---

## 🐳 Docker Deployment (Recommended)

This project is fully containerized. A single command builds, configures, and binds the SQLite database, backend APIs, frontend, and a web-based database viewer.

### 1. Launch the Stack
Start the containerized stack in detached mode:
```bash
make up
```

This starts three services:
* **Backend API Gateway (FastAPI):** Exposes port `8000`. For detailed APIs document [APIs.md](APIs.md)
* **Administration Dashboard (Streamlit):** Exposes port `8501`.
* **Database Administrator (phpLiteAdmin):** Exposes port `8082`.

### 2. Expose the Local Port via LocalTunnel
To allow Telegram's servers to send webhook events to your local container, you must expose port `8000` using a public gateway:
```bash
make tunnel
```
*(Keep this terminal open. It should display your dynamic public URL, e.g., `https://ai-grandchild-vn.loca.lt`).*

### 3. Register the Webhook
In a new terminal window, register your active public tunnel URL with the Telegram Bot API:
```bash
make set-telegram-webhook
```
Verify the output displays: `Telegram API Response: {'ok': True, 'result': True, ...}`.

---

## 🛠️ Local Development (Alternative)

If you prefer to run the services directly on your host machine without Docker:

```bash
# 1. Sync local python dependencies inside your virtual environment
make init

# 2. Run the FastAPI server in Terminal 1
make server

# 3. Run the Streamlit Dashboard in Terminal 2
make dashboard

# 4. Start LocalTunnel and register webhooks in Terminal 3 & 4
make tunnel
make set-telegram-webhook
```

---

## ⚙️ Admin Operations & Testing

### 1. Set Up Your SQLite Whitelist
Because the database begins empty, you must first register your families and authorize your target chat IDs:

1. Open your web browser to the Admin Dashboard: **`http://localhost:8501`**.
2. Log in using the default credentials:
   * **Username:** `admin`
   * **Password:** `admin`
3. Go to the **🏠 Manage Families** tab and register a family directory (e.g., `God of War Family`).
4. Go to the **👥 Manage Members** tab:
   * **Add Senior:** Register Grandpa's real Telegram Chat ID, configure their role classification to `senior`, role identity to `grandpa`, and optionally link a **Bank Account** (e.g., `987654321`).
   * **Add Family Member:** Register the Family Member's real Telegram Chat ID, configure their role classification to `non_senior`, and role identity to `son` or `daughter`.

### 2. Test Live Chats on Telegram
* **As Grandpa:** Send a message to your bot (e.g., *"Those travel agency folks are so polite, they gave me a free 5-star lunch voucher!"*). The bot will reply with context-aware, warm grandchild advice.
* **As Family Member:** Message the bot to receive professional status updates.

### 3. Simulate Bank Webhook Events (Via Postman)
You can simulate automated bank transaction triggers on behalf of your Senior using Postman.
* **Method:** `POST`
* **URL:** `https://ai-grandchild-vn.loca.lt/test/bank_sms_webhook` (or `http://localhost:8000/test/bank_sms_webhook` if testing locally)
* **Headers:** `Content-Type: application/json`
* **JSON Body:**
  ```json
  {
    "bank_app_id": "hsbc_vn",
    "bank_account": "987654321",
    "transaction_id": "TXN_9821038201",
    "sms_content": "Acct 987654321: -50,000,000 VND tai CONG TY DU LICH TOAN CAU vào lúc 14:30. So CCCD cua ngoai la 123456789. So TK ngan hang la 987654321."
  }
  ```
When sent, the backend maps the account number to your Grandpa, executes the risk analysis, scrubs the SSN, replies to Grandpa, and dispatches the high-risk alert directly to the Family Member's Telegram chat.

### 4. Inspect SQLite Relational Data
You can inspect, query, and manage your raw database tables (`families`, `members`, `chat_messages`) in your browser.
* **URL:** **`http://localhost:8082`**
* **Password:** `admin`
* Select `ai_grandchild.db` on the left panel to browse tables.

### 5. Check Logs and Shutdown
```bash
# Stream background logs (Agent trace logs, SQL executions, and web traffic)
make logs

# Stop and clean up all containers safely
make down
```
