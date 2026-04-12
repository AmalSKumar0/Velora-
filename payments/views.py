import json

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from payments.services.payment_service import PaymentService
from commissions.models import Order
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def create_payment(request, order_id):
    order = Order.objects.get(id=order_id)

    service = PaymentService()
    payment, razorpay_order = service.create_order(order, order.amount)

    return render(request, "client/request/payment.html", {
        "order_id": razorpay_order["id"],
        "key": settings.RAZORPAY_KEY_ID,
        "amount": order.amount
    })

@csrf_exempt  
@require_POST
def verify_payment(request):
    try:
        data = json.loads(request.body)

        service = PaymentService()

        payment = service.verify_and_capture(data)

        if payment is None:
            return JsonResponse({
                "status": "error",
                "message": "Payment not found"
            }, status=404)

        return JsonResponse({
            "status": "success",
            "payment_status": payment.status
        })

    except Exception as e:
        return JsonResponse({
            "status": "failed",
            "message": str(e)
        }, status=400)