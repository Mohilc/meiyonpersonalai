"""Webhook endpoints for Telegram and WhatsApp live messaging."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, Form, Header
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.services import messaging_bot_service

router = APIRouter(prefix="/api/webhooks", tags=["Messaging Webhooks"])

@router.get("/status")
def get_messaging_status():
    """Checks the status of Telegram and WhatsApp messaging connections."""
    return {
        "telegram": {
            "enabled": settings.TELEGRAM_ENABLED,
            "configured": bool(settings.TELEGRAM_BOT_TOKEN),
            "allowed_chat_id_set": bool(settings.TELEGRAM_ALLOWED_CHAT_ID)
        },
        "whatsapp": {
            "enabled": settings.WHATSAPP_ENABLED,
            "twilio_configured": bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN),
            "allowed_number_set": bool(settings.WHATSAPP_ALLOWED_NUMBER)
        }
    }

@router.post("/telegram")
async def telegram_webhook(request: Request):
    """Processes incoming Telegram message webhooks."""
    data = await request.json()
    message = data.get("message", {})
    chat = message.get("chat", {})
    chat_id = str(chat.get("id", ""))
    text = message.get("text", "")

    if chat_id and text:
        reply = messaging_bot_service.handle_incoming_text(sender_id=chat_id, platform="telegram", text=text)
        messaging_bot_service.send_telegram_message(chat_id=chat_id, text=reply)

    return {"status": "OK"}

@router.post("/whatsapp")
async def whatsapp_twilio_webhook(
    From: Optional[str] = Form(None),
    Body: Optional[str] = Form(None)
):
    """
    Processes incoming WhatsApp messages from Twilio.
    Returns standard TwiML XML response.
    """
    sender = From or ""
    incoming_text = Body or ""

    if not sender or not incoming_text:
        return PlainTextResponse("<Response></Response>", media_type="text/xml")

    reply_text = messaging_bot_service.handle_incoming_text(sender_id=sender, platform="whatsapp", text=incoming_text)
    
    # Return TwiML response
    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Response>\n'
        f'    <Message>{reply_text}</Message>\n'
        '</Response>'
    )
    return Response(content=twiml, media_type="text/xml")
