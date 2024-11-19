from django.views import View
from django.http import JsonResponse
from django.views.generic import ListView

from school.models import Sinf, Maktab, Belgisi
import json


class AddClassAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            # POST ma'lumotlarini olish
            data = json.loads(request.body)
            maktab_id = data.get('maktab')
            sinf_raqami = data.get('sinf_raqami')
            belgi_nomi = data.get('belgi')  # Belgini kiritish

            if not all([maktab_id, sinf_raqami, belgi_nomi]):
                return JsonResponse({'success': False, 'message': 'Barcha maydonlarni to\'ldiring.'}, status=400)

            # Maktab mavjudligini tekshirish
            maktab = Maktab.objects.filter(id=maktab_id).first()
            if not maktab:
                return JsonResponse({'success': False, 'message': 'Tanlangan maktab mavjud emas.'}, status=400)

            # Belgini katta harfga o'zgartirish
            belgi_nomi = belgi_nomi.upper()

            # Belgini bazadan qidirish yoki yaratish
            belgi, created = Belgisi.objects.get_or_create(
                nomi=belgi_nomi,
                defaults={'is_active': True}
            )

            # Yangi sinfni yaratish
            sinf = Sinf.objects.create(
                maktab=maktab,
                sinf_raqami=sinf_raqami,
                belgisi=belgi,
                is_active=True
            )
            return JsonResponse({'success': True, 'message': 'Sinf muvaffaqiyatli qo\'shildi!', 'sinf_id': sinf.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'}, status=500)


class StatsClassAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Statistikani hisoblash
            total_classes = Sinf.objects.count()
            total_schools = Maktab.objects.count()

            return JsonResponse({
                'success': True,
                'stats': {
                    'total_classes': total_classes,
                    'total_schools': total_schools
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Xatolik yuz berdi: {str(e)}"
            }, status=500)


class SchoolTableView(ListView):
    model = Maktab

    context_object_name = 'schools'

    def get_queryset(self):
        return Maktab.objects.select_related('viloyat', 'tuman').all()

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            schools = [
                {
                    'viloyat': school.viloyat.name if school.viloyat else 'Noma\'lum',
                    'tuman': school.tuman.name if school.tuman else 'Noma\'lum',
                    'maktab_raqami': school.maktab_raqami,
                    'created_at': school.created_at.strftime('%Y-%m-%d %H:%M'),
                }
                for school in context['schools']
            ]
            return JsonResponse({'success': True, 'schools': schools})
        return super().render_to_response(context, **response_kwargs)

class ClassListAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            classes = Sinf.objects.select_related('maktab', 'belgisi').all()
            data = [
                {
                    'id': cls.id,
                    'sinf_raqami': cls.sinf_raqami,
                    'belgi': cls.belgisi.nomi if cls.belgisi else "Belgisi yo'q",
                    'maktab': {
                        'id': cls.maktab.id,
                        'raqami': cls.maktab.maktab_raqami,
                        'viloyat': cls.maktab.viloyat.name if cls.maktab.viloyat else "Viloyat yo'q",
                        'tuman': cls.maktab.tuman.name if cls.maktab.tuman else "Tuman yo'q",
                    },
                    'is_active': cls.is_active,
                    'created_at': cls.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for cls in classes
            ]
            return JsonResponse({'success': True, 'classes': data})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
