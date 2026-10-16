"""Send WhatsApp Message or Test Interactive Chat with Meiyon."""
import os
import sys
import argparse
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

def run_interactive_simulation(sender_number: str):
    """Interactive terminal chat simulating WhatsApp channel."""
    from app.services import messaging_bot_service
    print("\n" + "="*60)
    print("💬 MEIYON WHATSAPP SIMULATOR (Two-Way Interactive Chat)")
    print(f"📱 Channel: WhatsApp | Sender: {sender_number}")
    print("Type your message below (or 'exit' / 'quit' to stop):")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("👋 Exiting WhatsApp simulator. Goodbye!")
                break
                
            reply = messaging_bot_service.handle_incoming_text(
                sender_id=sender_number,
                platform="whatsapp",
                text=user_input
            )
            print(f"\nMeiyon [WhatsApp] >\n{reply}\n")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting WhatsApp simulator.")
            break

def main():
    parser = argparse.ArgumentParser(description="WhatsApp Dispatch & Interactive AI Tester")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive WhatsApp terminal chat simulation")
    parser.add_argument("--text", "-t", type=str, default="", help="Direct text body to send instead of Content Template")
    parser.add_argument("--to", type=str, default="", help="Recipient phone number (e.g., +918590144798)")
    args = parser.parse_args()

    to_number = args.to or os.environ.get("WHATSAPP_ALLOWED_NUMBER", "+918590144798")

    if args.interactive:
        run_interactive_simulation(to_number)
        return

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+17372508034")
    content_sid = os.environ.get("TWILIO_CONTENT_SID", "HXfe5ab5f00277942d4d4200328b4d403c")

    if not (account_sid and auth_token):
        print("⚠️ Warning: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is not yet set in .env.")
        print("👉 Falling back to interactive WhatsApp chat mode so you can talk to Meiyon immediately!")
        run_interactive_simulation(to_number)
        return

    # Format whatsapp: prefix
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        print(f"📡 Sending WhatsApp message via Twilio...")
        print(f"   From: {from_number}")
        print(f"   To:   {to_number}")

        if args.text:
            print(f"   Body: {args.text}")
            message = client.messages.create(
                to=to_number,
                from_=from_number,
                body=args.text
            )
        else:
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

if __name__ == "__main__":
    main()
