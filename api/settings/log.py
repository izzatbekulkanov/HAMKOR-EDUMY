# views.py
from django.http import JsonResponse
from django.views import View
from account.models import UserActivity
from django.core.serializers import serialize


class UserActivityLogView(View):
    def get(self, request):
        activities = UserActivity.objects.select_related('user').all()
        activity_logs = []

        for activity in activities:
            user = activity.user
            activity_logs.append({
                "id": activity.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.second_name,
                "phone": user.phone_number,
                "login_time": activity.login_time,
                "logout_time": activity.logout_time
            })

        return JsonResponse(activity_logs, safe=False)
