"""
Webhook endpoints.

- Resend: Email
"""

import logging

import resend
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.settings import get_settings
from task.celery_worker import process_email_received

settings = get_settings()

logger = logging.getLogger(f'uvicorn.{settings.app_name}.webhook')

router = APIRouter()

resend.api_key = settings.resend_api_key.get_secret_value()


@router.post('/resend/')
async def resend_webhook(request: Request) -> JSONResponse:
    raw_data = await request.body()

    # Extract Svix headers
    headers: resend.WebhookHeaders = {
        'id': request.headers.get('svix-id', ''),
        'timestamp': request.headers.get('svix-timestamp', ''),
        'signature': request.headers.get('svix-signature', ''),
    }

    # Verify the webhook
    try:
        resend.Webhooks.verify(
            {
                'payload': raw_data.decode('utf-8'),
                'headers': headers,
                'webhook_secret': settings.resend_webhook_secret.get_secret_value(),
            }
        )
    except ValueError:
        return JSONResponse({'error': 'Webhook verification failed'}, status_code=400)

    json_data = await request.json()
    event_type = json_data['type']
    match event_type:
        case 'email.received':
            email_id = json_data['data']['email_id']
            email_from = json_data['data']['from']
            logger.info(f'Email received [{email_id}] from {email_from}')
            process_email_received.delay(json_data)
        case _:
            pass

    return JSONResponse({'success': True})
