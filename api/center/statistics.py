from django.http import JsonResponse
from django.views import View
from center.models import Center, Filial, Kasb, Yonalish, Kurs, E_groups, GroupMembership
from django.db.models import Count, Sum, F
from datetime import datetime, timedelta


class StatisticsDashboardView(View):
    def get(self, request):
        today = datetime.now()
        last_month = today - timedelta(days=30)
        last_year = today - timedelta(days=365)

        # Filial Statistics
        filial_stats = {
            "total": Filial.objects.count(),
            "today": Filial.objects.filter(created_at__date=today.date()).count(),
            "last_month": Filial.objects.filter(created_at__gte=last_month).count(),
            "last_year": Filial.objects.filter(created_at__gte=last_year).count(),
            "locations": list(Filial.objects.values("location", "contact", "telegram")),
        }

        # Kasb Statistics
        kasb_stats = {
            "total": Kasb.objects.count(),
            "active": Kasb.objects.filter(is_active=True).count(),
            "recent": list(Kasb.objects.order_by("-created_at")[:5].values("nomi", "created_at")),
        }

        # Yonalish Statistics
        yonalish_stats = {
            "total": Yonalish.objects.count(),
            "active": Yonalish.objects.filter(is_active=True).count(),
            "kasb_distribution": list(
                Yonalish.objects.values("kasb__nomi").annotate(count=Count("id")).order_by("-count")
            ),
        }

        # Kurs Statistics
        kurs_stats = {
            "total": Kurs.objects.count(),
            "total_revenue": Kurs.objects.aggregate(Sum("narxi"))["narxi__sum"] or 0,
            "recent_courses": list(
                Kurs.objects.order_by("-created_at").values("nomi", "narxi", "created_at")[:5]
            ),
        }

        # Group Statistics
        group_stats = {
            "total": E_groups.objects.count(),
            "active_groups": E_groups.objects.filter(is_active=True).count(),
            "students_total": GroupMembership.objects.count(),
            "group_revenue": E_groups.objects.annotate(group_revenue=F("kurs__narxi"))
            .aggregate(total_revenue=Sum("group_revenue"))["total_revenue"]
            or 0,
            "recent_groups": list(
                E_groups.objects.order_by("-created_at").values(
                    "group_name", "kurs__nomi", "created_at", "is_active"
                )[:5]
            ),
        }

        # Student Statistics in Groups
        group_student_distribution = list(
            GroupMembership.objects.values("group__group_name")
            .annotate(student_count=Count("student"))
            .order_by("-student_count")
        )

        # Weekly Class Schedule
        weekly_schedule = list(
            E_groups.objects.values("group_name", "days_of_week", "kurs__nomi")
        )

        # Aggregated Data
        data = {
            "branches": filial_stats,
            "professions": kasb_stats,
            "fields": yonalish_stats,
            "courses": kurs_stats,
            "groups": group_stats,
            "group_student_distribution": group_student_distribution,
            "weekly_schedule": weekly_schedule,
        }

        return JsonResponse({"success": True, "data": data})
