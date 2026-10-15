# Step-by-Step Guide: Connecting Gmail & LinkedIn MCP

This guide explains how to connect your real **Gmail** and **LinkedIn** accounts to your Personal AI Manager and the Antigravity IDE.

---

## 1. Create your `.env` File

In PowerShell inside `c:\Users\MOHIL\Desktop\agenticai`:
```powershell
Copy-Item .env.example .env
```

---

## 2. Connect Your Real Gmail (Takes 2 minutes)

Google requires an **App Password** for automated IMAP/SMTP access:

1. Open [https://myaccount.google.com/security](https://myaccount.google.com/security) in your browser.
2. Ensure **2-Step Verification** is turned **ON**.
3. Open [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
4. Enter App name: `Personal AI Manager` and click **Create**.
5. Copy the 16-character password (e.g. `abcd efgh ijkl mnop`).
6. Open your `.env` file and fill in:
   ```env
   GMAIL_ADDRESS="your_email@gmail.com"
   GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
   ```

---

## 3. Connect Your Real LinkedIn (Takes 1 minute)

Because LinkedIn personal messaging doesn't have a public API, your MCP server uses Playwright browser automation with your session cookie (`li_at`):

1. Open [https://www.linkedin.com](https://www.linkedin.com) in Chrome or Edge and make sure you are logged in.
2. Press **`F12`** (Inspect Element).
3. Click the **Application** tab at the top (or click `>>` if hidden).
4. On the left menu, expand **Storage** -> **Cookies** -> `https://www.linkedin.com`.
5. Find the cookie named **`li_at`**.
6. Double-click its **Value** and copy it.
7. Open your `.env` file and paste it:
   ```env
   LINKEDIN_LI_AT_COOKIE="AQED..."
   LINKEDIN_HEADLESS="true"
   ```

---

## 4. How to Test Your Connection

### Option A: Via Web Dashboard
1. Start the server:
   ```powershell
   .\run.ps1
   ```
2. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
3. Click **Communications & MCP** in the left sidebar.
4. Click **↻ Sync Gmail (MCP)** or **↻ Sync LinkedIn (MCP)**!

### Option B: Ask the Antigravity IDE Agent
You can simply type in chat:
- *"Check my unread recruiter emails using MCP"*
- *"Check my LinkedIn connection requests using MCP"*

The AI assistant will execute the tools through `.agents/mcp_config.json` automatically!
