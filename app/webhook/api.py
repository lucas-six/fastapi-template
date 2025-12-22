"""
Webhook endpoints.

- Resend: Email
"""

import logging

import resend
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.dependencies import get_redis_session
from app.settings import get_settings
from app.utils import pid_str
from task.celery_worker import handle_resend_email_received

settings = get_settings()

logger = logging.getLogger(f'uvicorn.{settings.app_name}.webhook')

router = APIRouter()

resend.api_key = settings.resend_api_key.get_secret_value()


@router.post('/resend/')
async def resend_webhook(
    request: Request, redis_session: Redis = Depends(get_redis_session)
) -> JSONResponse:
    logger.debug(f'Resend webhook endpoint [{await pid_str()}]...')

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
    task = None
    match event_type:
        case 'email.received':
            email_id = json_data['data']['email_id']
            email_from = json_data['data']['from']
            logger.info(f'Email received [{email_id}] from {email_from}')
            task = handle_resend_email_received.delay(json_data)
            logger.debug(f'Email received task {task.id} delayed')
        case _:
            pass

    # Add to Redis Streams for other services to consume
    if settings.resend_webhook_publish_to_redis:
        await redis_session.xadd(
            f'{settings.cache_prefix}:webhook:resend',
            json_data,
            maxlen=settings.resend_webhook_queue_maxlen,
        )
        logger.debug(f'Resend webhook data added to Redis [{await pid_str()}]...')

    rsp = {'success': True}
    if task:
        rsp['task_id'] = task.id
    return JSONResponse(rsp)
