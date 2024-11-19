from django.http import JsonResponse
from django.views import View
from center.models import Kurs, E_groups, Kasb, Yonalish
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class GroupListView(View):
    def get(self, request):
        groups = E_groups.objects.select_related('kurs__yonalish__kasb').all().order_by('-created_at')
        data = [
            {
                'id': group.id,
                'group_name': group.group_name,
                'kurs': {
                    'id': group.kurs.id,
                    'nomi': group.kurs.nomi,
                    'narxi': group.kurs.narxi
                },
                'yonalish': {
                    'id': group.kurs.yonalish.id,
                    'nomi': group.kurs.yonalish.nomi
                },
                'kasb': {
                    'id': group.kurs.yonalish.kasb.id,
                    'nomi': group.kurs.yonalish.kasb.nomi
                },
                'days_of_week': group.days_of_week,
                'days_of_week_display': group.get_days_of_week_display(),
                'is_active': group.is_active,
                'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': group.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for group in groups
        ]
        return JsonResponse({'success': True, 'data': data})

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            group_name = data.get('group_name')
            kurs_id = data.get('kurs')
            days_of_week = data.get('days_of_week', [])

            if not group_name or not kurs_id:
                return JsonResponse({'success': False, 'message': 'Guruh nomi va kurs majburiy.'}, status=400)

            kurs = Kurs.objects.get(id=kurs_id)
            group = E_groups.objects.create(
                group_name=group_name,
                kurs=kurs,
                days_of_week=days_of_week
            )
            return JsonResponse({'success': True, 'message': 'Guruh muvaffaqiyatli qo\'shildi!'})
        except Kurs.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Kurs topilmadi.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


class KasbFilterView(View):
    def get(self, request):
        kasblar = Kasb.objects.all()
        data = [{'id': kasb.id, 'nomi': kasb.nomi} for kasb in kasblar]
        return JsonResponse({'success': True, 'data': data})


class YonalishFilterView(View):
    def get(self, request):
        kasb_id = request.GET.get('kasb_id')
        yonalishlar = Yonalish.objects.filter(kasb_id=kasb_id).prefetch_related('kurslar')
        data = [
            {
                'id': yonalish.id,
                'nomi': yonalish.nomi,
                'kurs_count': yonalish.kurslar.count()
            }
            for yonalish in yonalishlar
        ]
        return JsonResponse({'success': True, 'data': data})


class KursFilterView(View):
    def get(self, request):
        yonalish_id = request.GET.get('yonalish_id')
        kurslar = Kurs.objects.filter(yonalish_id=yonalish_id)
        data = [{'id': kurs.id, 'nomi': kurs.nomi, 'narxi': kurs.narxi} for kurs in kurslar]
        return JsonResponse({'success': True, 'data': data})
