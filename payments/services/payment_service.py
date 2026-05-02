import razorpay
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from payments.models import Payment
from commissions.models import Order, Proposal, Request

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

        # Create Razorpay order only once
        if not payment.provider_order_id:
            razorpay_order = self.client.order.create({
                "amount": amount * 100,  # paise
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
    # VERIFY PAYMENT
    # ----------------------------
    def verify_and_capture(self, data):

        logger.info(f"Verifying payment: {data}")

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")

        # 1. Signature verification (secure)
        try:
            self.client.utility.verify_payment_signature(data)
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return None

        # 2. Fetch payment from Razorpay
        payment_data = self.client.payment.fetch(payment_id)

        # 3. SECURITY CHECK → ensure payment belongs to order
        if payment_data.get("order_id") != order_id:
            logger.error("Payment does not belong to this order")
            return None

        # 4. Validate payment status
        if payment_data["status"] not in ["captured", "authorized"]:
            logger.warning(f"Payment not successful: {payment_id}")
            return self.mark_failed(order_id, payment_data)

        return self.mark_held(order_id, payment_id, payment_data)

    # ----------------------------
    # MARK AS HELD (ESCROW START)
    # ----------------------------
    @transaction.atomic
    def mark_held(self, provider_order_id, payment_id, payload):

        try:
            payment = Payment.objects.select_for_update().get(
                provider_order_id=provider_order_id
            )
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {provider_order_id}")
            return None

        # Idempotency
        if payment.status != Payment.Status.PENDING:
            return payment

        # Update payment
        payment.provider_payment_id = payment_id
        payment.status = Payment.Status.HELD
        payment.save()

        # Get related objects
        order = payment.order
        req = order.request
        proposal = order.proposal

        order.status = Order.Status.IN_PROGRESS
        order.save()

        # Accept proposal
        proposal.status = Proposal.Status.ACCEPTED
        proposal.save()

        # Reject others
        Proposal.objects.filter(
            request=req
        ).exclude(id=proposal.id).update(status=Proposal.Status.REJECTED)

        # Update request
        req.status = Request.Status.IN_PROGRESS
        req.save()

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

        # If already completed, don't downgrade
        if payment.status == Payment.Status.HELD:
            return payment

        payment.status = Payment.Status.FAILED
        payment.save()

        # Optional: mark order cancelled
        order = payment.order
        order.status = Order.Status.CANCELLED
        order.save()

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

        # NOTE: manual transfer required (Razorpay Route for automation)

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
        self.client.payment.refund(payment.provider_payment_id, {"amount": int(payment.amount * 100)})

        payment.status = Payment.Status.REFUNDED
        payment.refunded_at = timezone.now()
        payment.save()

        # Update order
        order.status = Order.Status.CANCELLED
        order.save()

        logger.info(f"Payment REFUNDED for order={order.id}")
        return payment