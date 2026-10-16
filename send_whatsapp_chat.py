"""Send WhatsApp Template Message using Twilio Content API."""
import os
import sys
from pathlib import Path

# Automatically read from .env if environment variables are not globally exported
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ and v:
                    os.environ[k] = v

account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
to_number = os.environ.get("WHATSAPP_ALLOWED_NUMBER", "+918590144798")
from_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+17372508034")
content_sid = os.environ.get("TWILIO_CONTENT_SID", "HXfe5ab5f00277942d4d4200328b4d403c")

# Format whatsapp: prefix
if not to_number.startswith("whatsapp:"):
    to_number = f"whatsapp:{to_number}"
if not from_number.startswith("whatsapp:"):
    from_number = f"whatsapp:{from_number}"

if not (account_sid and auth_token):
    print("❌ Error: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is not set.")
    print("👉 Please open your .env file and set:")
    print("   TWILIO_ACCOUNT_SID=\"AC...\"")
    print("   TWILIO_AUTH_TOKEN=\"your_auth_token\"")
    sys.exit(1)

try:
    from twilio.rest import Client

    client = Client(account_sid, auth_token)

    print(f"📡 Sending WhatsApp message via Twilio...")
    print(f"   From: {from_number}")
    print(f"   To:   {to_number}")
    print(f"   Content SID: {content_sid}")

    message = client.messages.create(
        to=to_number,
        from_=from_number,
        content_sid=content_sid,
    )

    print(f"✅ Success! Message SID: {message.sid}")
    print(f"   Status: {message.status}")
    print(f"💬 You can now reply on WhatsApp to chat directly with Meiyon!")
except Exception as e:
    print(f"❌ Failed to dispatch message: {str(e)}")
    sys.exit(1)
