import razorpay
import hmac
import hashlib
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from payments.models import Payment

logger = logging.getLogger(__name__)


class InvalidPaymentState(Exception):
    pass


class PaymentService:

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    # ----------------------------
    # CREATE ORDER (INIT PAYMENT)
    # ----------------------------
    def create_order(self, order, amount):

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "amount": amount,
                "status": Payment.Status.PENDING,
                "provider": "razorpay",
            }
        )

        if not payment.provider_order_id:
            razorpay_order = self.client.order.create({
                "amount": amount * 100,
                "currency": "INR"
            })

            payment.provider_order_id = razorpay_order["id"]
            payment.save()
        else:
            razorpay_order = {
                "id": payment.provider_order_id
            }

        return payment, razorpay_order

    # ----------------------------
    # VERIFY PAYMENT (API FLOW)
    # ----------------------------
    def verify_and_capture(self, data):
        """
        Called after frontend handler sends payment response
        """

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        # STEP 1: signature verification
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{order_id}|{payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != signature:
            logger.warning("Invalid payment signature")
            raise Exception("Invalid signature")

        # STEP 2: fetch from Razorpay
        payment_data = self.client.payment.fetch(payment_id)

        if payment_data["status"] != "captured":
            logger.warning(f"Payment not captured: {payment_id}")
            return self.mark_failed(order_id, payment_data)

        # STEP 3: mark as HELD (escrow)
        return self.mark_held(order_id, payment_id, payment_data)

    # ----------------------------
    # MARK AS HELD (ESCROW START)
    # ----------------------------
    @transaction.atomic
    def mark_held(self, provider_order_id, payment_id, payload):
        """
        Move payment to HELD (money received, escrow state)
        """

        try:
            payment = Payment.objects.select_for_update().get(
                provider_order_id=provider_order_id
            )
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {provider_order_id}")
            return None

        if payment.status != Payment.Status.PENDING:
            return payment  # idempotent

        payment.provider_payment_id = payment_id
        payment.status = Payment.Status.HELD
        payment.save()

        logger.info(f"Payment HELD: {provider_order_id}")
        return payment

    # ----------------------------
    # MARK FAILED
    # ----------------------------
    @transaction.atomic
    def mark_failed(self, provider_order_id, payload):
        try:
            payment = Payment.objects.select_for_update().get(
                provider_order_id=provider_order_id
            )
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {provider_order_id}")
            return None

        if payment.status == Payment.Status.HELD:
            return payment  # don't downgrade

        payment.status = Payment.Status.FAILED
        payment.save()

        logger.info(f"Payment FAILED: {provider_order_id}")
        return payment

    # ----------------------------
    # RELEASE (ESCROW → ARTIST)
    # ----------------------------
    @transaction.atomic
    def release_payment(self, order):
        payment = Payment.objects.select_for_update().get(order=order)

        if payment.status != Payment.Status.HELD:
            raise InvalidPaymentState("Payment is not in escrow")

        # NOTE:
        # Razorpay does NOT auto-transfer to artist.
        # You must implement payout separately (optional).

        payment.status = Payment.Status.RELEASED
        payment.released_at = timezone.now()
        payment.save()

        logger.info(f"Payment RELEASED for order={order.id}")
        return payment

    # ----------------------------
    # REFUND
    # ----------------------------
    @transaction.atomic
    def refund_payment(self, order):
        payment = Payment.objects.select_for_update().get(order=order)

        if payment.status != Payment.Status.HELD:
            raise InvalidPaymentState("Only held payments can be refunded")

        if not payment.provider_payment_id:
            raise Exception("No payment ID for refund")

        # Razorpay refund
        self.client.payment.refund(payment.provider_payment_id)

        payment.status = Payment.Status.REFUNDED
        payment.refunded_at = timezone.now()
        payment.save()

        logger.info(f"Payment REFUNDED for order={order.id}")
        return payment