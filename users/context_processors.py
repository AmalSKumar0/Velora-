from commissions.models import Dispute

def open_disputes_processor(request):
    if request.user.is_authenticated and request.user.is_superuser:
        count = Dispute.objects.filter(status='open').count()
        return {'open_disputes_count': count}
    return {}
