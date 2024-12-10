from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from school.models import Maktab
import json
from django.core.files.storage import default_storage
import re  # Regular expressions uchun


@csrf_exempt
def list_schools(request):
    """
    Maktablar ro'yxatini qaytarish.
    """
    if request.method == "GET":
        schools = Maktab.objects.filter(is_active=True).order_by("-created_at")
        data = [
            {
                "id": school.id,
                "viloyat": school.viloyat,
                "tuman": school.tuman,
                "maktab_raqami": school.maktab_raqami,
                "sharntoma_raqam": school.sharntoma_raqam,
                "nomi": school.nomi,
            }
            for school in schools
        ]
        return JsonResponse(data, safe=False, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def add_school(request):
    """
    Yangi maktab qo'shish.
    """
    if request.method == "POST":
        try:
            # FormData yordamida ma'lumotlarni olish
            if request.content_type == "application/json":
                # Agar JSON formatda kelgan bo'lsa
                data = json.loads(request.body)
            else:
                # Agar FormData formatida kelgan bo'lsa
                data = request.POST

            # Kiritilgan ma'lumotlarni olish
            viloyat = data.get("viloyat")
            tuman = data.get("tuman")
            maktab_raqami = data.get("maktab_raqami")
            sharntoma_raqam = data.get("sharntoma_raqam")
            nomi = data.get("nomi")

            # Barcha maydonlar to'ldirilganligini tekshirish
            if not (viloyat and tuman and maktab_raqami and sharntoma_raqam and nomi):
                return JsonResponse({"error": "Barcha maydonlar to'ldirilishi shart"}, status=400)

            # Yangi maktabni yaratish
            maktab = Maktab.objects.create(
                viloyat=viloyat,
                tuman=tuman,
                maktab_raqami=maktab_raqami,
                sharntoma_raqam=sharntoma_raqam,
                nomi=nomi,
            )
            return JsonResponse({"message": "Maktab muvaffaqiyatli qo'shildi", "id": maktab.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON formatida xatolik bor"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def get_schools_by(request):
    """
    Maktablarni viloyatlar va tumanlar bo'yicha guruhlab olish.
    """
    if request.method == "GET":
        try:
            grouped_data = (
                Maktab.objects
                .values('viloyat', 'tuman')
                .annotate(school_count=Count('id'))
                .order_by('viloyat', 'tuman')
            )

            result = {}
            for entry in grouped_data:
                viloyat = entry['viloyat']
                tuman = entry['tuman']
                if viloyat not in result:
                    result[viloyat] = {}

                result[viloyat][tuman] = {
                    "maktab_soni": entry['school_count'],
                    "maktablar": list(
                        Maktab.objects.filter(viloyat=viloyat, tuman=tuman).values(
                            'id', 'maktab_raqami', 'sharntoma_raqam', 'nomi'
                        )
                    )
                }
            return JsonResponse({"data": result}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)



@csrf_exempt
def delete_school(request, school_id):
    """
    Maktabni o'chirish.
    """
    if request.method == "DELETE":
        try:
            school = Maktab.objects.filter(id=school_id, is_active=True).first()
            if not school:
                return JsonResponse({"error": "Maktab topilmadi"}, status=404)

            school.is_active = False
            school.save()
            return JsonResponse({"message": "Maktab muvaffaqiyatli o'chirildi"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def extract_maktab_raqami_and_nom(maktab_nomi):
    """
    Maktab nomidan raqamni ajratish va "son" yoki "sonli" qo'shimchalarini olib tashlash.
    """
    match = re.match(r"^(\d+)\s*-\s*.*", maktab_nomi)
    if match:
        maktab_raqami = int(match.group(1))  # Raqamni ajratib olish
        nomi = re.sub(r"^\d+\s*-\s*", "", maktab_nomi).strip()  # Qolgan matnni tozalash
        # "son" yoki "sonli" qo'shimchalarini olib tashlash
        nomi = re.sub(r"(\bson\b|\bsonli\b)", "", nomi, flags=re.IGNORECASE).strip()
        return maktab_raqami, nomi
    # Agar raqam topilmasa, faqat nom qaytariladi
    nomi = re.sub(r"(\bson\b|\bsonli\b)", "", maktab_nomi, flags=re.IGNORECASE).strip()
    return None, nomi

@csrf_exempt
def bulk_add_schools(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            for item in data:
                maktab_raqami, nomi = extract_maktab_raqami_and_nom(item["maktab"])

                # Update if exists, otherwise create
                Maktab.objects.update_or_create(
                    viloyat=item["viloyat"],
                    tuman=item["tuman"],
                    maktab_raqami=maktab_raqami,
                    defaults={
                        "nomi": nomi,
                        "sharntoma_raqam": item.get("sharntoma_raqam"),
                    }
                )

            return JsonResponse({"message": "Maktablar muvaffaqiyatli saqlandi."}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=400)


@csrf_exempt
def analyze_json_file(request):
    file_path = request.GET.get("file")
    if not file_path:
        return JsonResponse({"error": "Fayl yo'li ko'rsatilmagan"}, status=400)

    try:
        file_path = default_storage.path(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        viloyatlar = set(item["viloyat"] for item in data)
        tumanlar = set(item["tuman"] for item in data)
        maktablar = len(data)

        return JsonResponse({"viloyatlar": len(viloyatlar), "tumanlar": len(tumanlar), "maktablar": maktablar}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
