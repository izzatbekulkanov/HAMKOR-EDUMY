import random

from django.views import View
from django.http import JsonResponse
from school.models import Maktab, Sinf, Belgisi, Regions, District
from django.db.utils import IntegrityError


class AddSchoolAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Formdan kelgan ma'lumotlarni olish
            viloyat_id = request.POST.get('viloyat')
            tuman_id = request.POST.get('tuman')
            maktab_raqami = request.POST.get('maktab_raqami')

            # Maydonlar to'ldirilganligini tekshirish
            if not all([viloyat_id, tuman_id, maktab_raqami]):
                return JsonResponse({'success': False, 'message': 'Barcha maydonlarni to\'ldiring.'}, status=400)

            # Shartnoma raqamini generatsiya qilish
            sharntoma_raqam = None
            while True:
                try:
                    # 7 xonali random raqam generatsiya qilish
                    sharntoma_raqam = random.randint(1000000, 9999999)
                    # Unikal ekanligini tekshirish
                    maktab = Maktab.objects.create(
                        viloyat_id=viloyat_id,
                        tuman_id=tuman_id,
                        maktab_raqami=maktab_raqami,
                        sharntoma_raqam=sharntoma_raqam,
                        is_active=True
                    )
                    break
                except IntegrityError:
                    # Agar raqam unikal bo'lmasa, qayta generatsiya qilish
                    continue

            return JsonResponse({'success': True, 'message': 'Maktab muvaffaqiyatli qo\'shildi!', 'sharntoma_raqam': sharntoma_raqam})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'}, status=500)


class SchoolListAPIView(View):
    def get(self, request, *args, **kwargs):
        schools = Maktab.objects.select_related('viloyat', 'tuman').all()  # 'sinfi' va 'belgisi' olib tashlandi
        school_data = [
            {
                'id': school.id,
                'viloyat': school.viloyat.name if school.viloyat else None,
                'tuman': school.tuman.name if school.tuman else None,
                'maktab_raqami': school.maktab_raqami,
                'is_active': school.is_active,
                'created_at': school.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for school in schools
        ]
        return JsonResponse({'success': True, 'schools': school_data})


# Viloyat va tumanlarni qaytarish uchun API
class RegionDistrictAPIView(View):
    def get(self, request, *args, **kwargs):
        regions = Regions.objects.values('id', 'name')
        districts = District.objects.values('id', 'region_id', 'name')
        return JsonResponse({'success': True, 'regions': list(regions), 'districts': list(districts)})


# Sinf va belgilarni qaytarish uchun API
class ClassBadgeAPIView(View):
    def get(self, request, *args, **kwargs):
        classes = Sinf.objects.values('id', 'nomi')
        badges = Belgisi.objects.values('id', 'nomi')
        return JsonResponse({'success': True, 'classes': list(classes), 'badges': list(badges)})
