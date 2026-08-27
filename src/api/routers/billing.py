from fastapi import APIRouter, Depends
from src.api.dependencies.auth import get_current_user_id
from src.common.enums import SubscriptionLevel, SubscriptionStatus
from src.api.dependencies.billing import get_payment_service, get_subscription_service
from src.api.services.subscription_service import SubscriptionService
from src.api.services.payment_service import PaymentService
from fastapi.responses import JSONResponse
from src.common.billing.plans import PLANS

billing_router = APIRouter(prefix="/billing")


@billing_router.get("/plans", description="Узнать стоимость планов.")
def plans() -> JSONResponse:
    return JSONResponse(content={str(level.value): float(plan.price) for (level, plan) in PLANS.items()}, status_code=200)


@billing_router.get("/subscription", description="Получить информацию о текущем плане.")
async def subscription(
    current_user_id: int = Depends(get_current_user_id),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> JSONResponse:
    active = await subscription_service.get_active(current_user_id)
    message = {"success": True, "level": active.level.value, "status": active.status.value, "start_at": str(active.start_at) if active.start_at is not None else None, "end_at": str(active.end_at) if active.end_at is not None else None}
    return JSONResponse(content=message, status_code=200)


@billing_router.post("/checkout", description="Сменить план.")
async def checkout(
    plan: SubscriptionLevel,
    current_user_id: int = Depends(get_current_user_id),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> JSONResponse:
    confirm_url = await subscription_service.checkout(current_user_id, plan)
    return JSONResponse(content={"success": True, "confirm_url": confirm_url}, status_code=200)


