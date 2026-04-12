import json

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from payments.services.payment_service import PaymentService
from commissions.models import Order
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user)

    service = PaymentService()
    payment, razorpay_order = service.create_order(order, order.amount)

    return render(request, "client/request/payment.html", {
        "order_id": razorpay_order["id"],
        "key": settings.RAZORPAY_KEY_ID,
        "amount": order.amount
    })


@login_required
@require_POST
def verify_payment(request):
    try:
        data = json.loads(request.body)

        service = PaymentService()
        payment = service.verify_and_capture(data)

        if payment is None:
            return JsonResponse({
                "status": "failed",
                "message": "Verification failed"
            }, status=400)

        return JsonResponse({
            "status": "success"
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)