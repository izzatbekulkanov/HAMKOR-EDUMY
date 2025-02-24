import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView

from center.models import PaymentOrder
from web_project import TemplateLayout
from django import forms
class PaymentCenterView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # 📌 **Filter qidirish bo‘yicha so‘rovlar**
        request = self.request
        status = request.GET.get("status", "")
        sender = request.GET.get("sender", "")
        receiver = request.GET.get("receiver", "")

        # 📌 **Barcha to‘lovlar**
        payments = PaymentOrder.objects.all()

        # 📌 **Filterlash**
        if status:
            payments = payments.filter(status=status)
        if sender:
            payments = payments.filter(sender__username__icontains=sender)
        if receiver:
            payments = payments.filter(receiver__username__icontains=receiver)

        # 📌 **Kontekstga qo‘shish**
        context.update({
            "payments": payments,
            "status_choices": PaymentOrder.STATUS_CHOICES,  # Statuslar ro‘yxati
        })
        return context



@csrf_exempt  # CSRF tekshirishni o‘chirish
@login_required
def create_payment_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = data.get("amount")
            card_number = data.get("card_number")

            if not  amount or not card_number:
                return JsonResponse({"error": "Barcha maydonlarni to‘ldiring"}, status=400)

            # Yangi to‘lov yaratish
            payment = PaymentOrder.objects.create(
                sender=request.user,
                amount=amount,
                card_number=card_number,
                status="pending"
            )

            return JsonResponse({"success": "To‘lov so‘rovi yaratildi", "payment_id": payment.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Noto‘g‘ri so‘rov turi"}, status=405)
