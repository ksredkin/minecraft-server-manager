from fastapi import APIRouter, Request, Response, Depends
from src.api.dependencies.billing import get_subscription_service
from src.api.services.subscription_service import SubscriptionService

webhook_router = APIRouter(prefix="/webhooks")


@webhook_router.post("/yookassa")
async def handle_yookassa_webhook(request: Request, subscription_service: SubscriptionService = Depends(get_subscription_service)) -> Response:
    data: dict[str, str|dict[str, str]] = await request.json()
    success = await subscription_service.handle_yookassa_webhook(data)
    return Response(status_code=200 if success else 400)
