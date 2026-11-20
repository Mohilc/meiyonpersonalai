# Connecting Google Drive to EmailAI Verification RAG

Follow these steps to connect your Google Drive reference folder to the Supabase pgvector verification system.

---

## 1. Create Your Reference Folder in Google Drive
1. Open [Google Drive](https://drive.google.com).
2. Create a dedicated folder (e.g., `EmailAI_Verification_Docs`).
3. Upload your reference documents into this folder:
   - `verified_enterprise_companies.txt` (Company names and official domains like `greenhouse.io`, `lever.co`, `workday.com`)
   - `recruiter_directory.json` (List of trusted recruiters and agency partners)
   - `scam_and_phishing_signatures.txt` (Known fraud phrases like cashier's check, crypto escrow, telegram redirects)
4. Open the folder in your browser and copy the **Folder ID** from the URL:
   - `https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J`
   - In this example, the Folder ID is: `1A2B3C4D5E6F7G8H9I0J`

---

## 2. Get a Google Cloud Service Account
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Select your project (or create a new one, e.g. `Meiyon-AI`).
3. Enable the **Google Drive API**:
   - Go to **APIs & Services > Library**.
   - Search for **Google Drive API** and click **Enable**.
4. Create a Service Account:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > Service Account**.
   - Name it `emailai-drive-sync` and click **Done**.
5. Generate a Key:
   - Click on the created service account email (e.g. `emailai-drive-sync@your-project.iam.gserviceaccount.com`).
   - Go to the **Keys** tab > **Add Key > Create new key > JSON**.
   - Download the JSON file to your computer.

---

## 3. Share Your Drive Folder with the Service Account
> [!IMPORTANT]
> The service account cannot see your folder until you share it.

1. Open your Google Drive folder.
2. Click **Share** (top right).
3. Paste the Service Account email address:
   `emailai-drive-sync@your-project.iam.gserviceaccount.com`
4. Set role to **Viewer** and click **Send**.

---

## 4. Configure Your `.env` File

Open your `.env` file in `agenticai/` and add the credentials:

### Option A: Local Development (Path to JSON)
```ini
GOOGLE_DRIVE_FOLDER_ID="1A2B3C4D5E6F7G8H9I0J"
GOOGLE_SERVICE_ACCOUNT_JSON="C:/Users/MOHIL/Desktop/agenticai/credentials/service_account.json"
```

### Option B: Cloud / Production / Render (Base64 Encoded)
Encode your JSON file in PowerShell:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("service_account.json"))
```
Then paste the string directly into `.env`:
```ini
GOOGLE_DRIVE_FOLDER_ID="1A2B3C4D5E6F7G8H9I0J"
GOOGLE_SERVICE_ACCOUNT_BASE64="eyJob3N0...=="
```

---

## 5. Run the Sync Trigger

Once your `.env` is updated, sync your documents into Supabase pgvector:

### Via Terminal:
```bash
uv run python scripts/sync_verification_drive.py
```

### Via HTTP API:
```bash
curl -X POST "http://localhost:8000/api/verification/sync-drive" \
  -H "x-sync-secret: meiyon-verification-sync-secret-key"
```

---

## How It Works During Live Messaging
- **Zero Drive Latency**: When an email or LinkedIn message arrives, Meiyon **never** connects to Google Drive.
- **Fast Supabase Query**: It queries only the indexed Supabase pgvector table, returning trust scores and risk flags in `< 5ms`.
