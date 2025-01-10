from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.views import View

from account.models import CashbackRecord


class GetNotificationsView(View):
    def get(self, request, *args, **kwargs):
        teacher = request.user

        if teacher.user_type != "2":  # Faqat o'qituvchilar uchun
            return JsonResponse({"success": False, "message": "Sizda bildirishnoma mavjud emas."}, status=400)

        cashback_records = CashbackRecord.objects.filter(
            teacher=teacher,
            is_viewed=False,
            updated_at__gte=now() - timedelta(days=1)
        ).select_related('student', 'cashback')

        notifications = []
        for record in cashback_records:
            student = record.student
            notifications.append({
                "student_name": f"{student.first_name} {student.last_name}",
                "cashback_amount": record.cashback.summasi,
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return JsonResponse({
            "success": True,
            "notifications": notifications,
            "has_unread": bool(cashback_records),
        })

    def post(self, request, *args, **kwargs):
        teacher = request.user

        CashbackRecord.objects.filter(
            teacher=teacher,
            is_viewed=False,
            updated_at__gte=now() - timedelta(days=1)
        ).update(is_viewed=True)

        return JsonResponse({"success": True, "message": "Barcha bildirishnomalar o'qildi."})
