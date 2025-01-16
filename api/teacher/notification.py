from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.views import View

from account.models import CashbackRecord


class GetNotificationsView(View):
    def get(self, request, *args, **kwargs):
        teacher = request.user
        print(f"GET so'rov qilindi. Foydalanuvchi: {teacher.username}, user_type: {teacher.user_type}")

        # Foydalanuvchi o'qituvchi emasligini tekshirish
        if teacher.user_type != "2":  # Faqat o'qituvchilar uchun
            print("Foydalanuvchi o'qituvchi emas.")
            return JsonResponse({
                "success": True,
                "notifications": [],  # Bo'sh bildirishnomalar ro'yxati
                "has_unread": False
            })

        cashback_records = CashbackRecord.objects.filter(
            teacher=teacher,
            is_viewed=False,
            updated_at__gte=now() - timedelta(days=1)
        ).select_related('student', 'cashback')

        print(f"Topilgan bildirishnomalar soni: {cashback_records.count()}")

        notifications = []
        for record in cashback_records:
            student = record.student
            print(f"Bildirishnoma uchun ma'lumot: Student: {student.first_name} {student.last_name}, Cashback: {record.cashback.summasi}, Created At: {record.created_at}")
            notifications.append({
                "student_name": f"{student.first_name} {student.last_name}",
                "cashback_amount": record.cashback.summasi,
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        print("Barcha bildirishnomalar: ", notifications)

        return JsonResponse({
            "success": True,
            "notifications": notifications,
            "has_unread": bool(cashback_records),
        })

    def post(self, request, *args, **kwargs):
        teacher = request.user
        print(f"POST so'rov qilindi. Foydalanuvchi: {teacher.username}")

        records_to_update = CashbackRecord.objects.filter(
            teacher=teacher,
            is_viewed=False,
            updated_at__gte=now() - timedelta(days=1)
        )

        print(f"Yangilanadigan bildirishnomalar soni: {records_to_update.count()}")

        records_to_update.update(is_viewed=True)

        print("Barcha bildirishnomalar o'qilgan deb belgilandi.")

        return JsonResponse({"success": True, "message": "Barcha bildirishnomalar o'qildi."})
