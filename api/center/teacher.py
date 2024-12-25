from django.http import JsonResponse
from center.models import SubmittedStudent, Sinf, Kasb, Yonalish, Filial, Kurs
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from school.models import Belgisi, Maktab
import json


@csrf_exempt
@login_required
def submit_student(request):
    if request.method == 'POST':
        # JSON formatidagi ma'lumotlarni olish
        try:
            data = json.loads(request.body)
            print(data)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Ma\'lumotlar formatida xatolik.'})

        # Form ma'lumotlarini JSONdan ajratib olish
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone')
        sinf_raqami = data.get('grade')  # sinf_raqami for Sinf
        kasb_id = data.get('profession')
        yonalish_id = data.get('field')
        belgisi_name = data.get('section')  # Belgisi name
        filial_id = data.get('branch')
        school_id = data.get('school')  # School ID
        course_ids = data.get('courses', [])  # List of course IDs

        # Debug: Print received data
        print(f"Received data: first_name={first_name}, last_name={last_name}, phone_number={phone_number}, "
              f"sinf_raqami={sinf_raqami}, kasb_id={kasb_id}, yonalish_id={yonalish_id}, "
              f"belgisi_name={belgisi_name}, filial_id={filial_id}, school_id={school_id}, courses={course_ids}")

        # Check if all required fields are provided
        if not all([first_name, last_name, phone_number, sinf_raqami, kasb_id, yonalish_id, belgisi_name, filial_id, school_id]):
            print("Error: Not all required fields are provided.")
            return JsonResponse({'status': 'error', 'message': 'Barcha maydonlarni to\'ldiring!'})

        try:
            # Check if a student with the same name and phone number already exists
            existing_student = SubmittedStudent.objects.filter(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number
            ).first()

            if existing_student:
                print(f"Found existing student: {existing_student}")
                return JsonResponse({'status': 'error', 'message': 'Bunday o\'quvchi allaqachon mavjud!'})

            # Get related objects
            kasb = Kasb.objects.get(id=kasb_id)
            yonalish = Yonalish.objects.get(id=yonalish_id)
            filial = Filial.objects.get(id=filial_id)
            school = Maktab.objects.get(id=school_id)

            # Fetch or create Belgisi
            belgisi, _ = Belgisi.objects.get_or_create(nomi=belgisi_name)

            # Fetch or create Sinf
            sinf_obj, created = Sinf.objects.get_or_create(
                maktab=school,
                sinf_raqami=sinf_raqami,
                defaults={
                    'belgisi': belgisi,
                    'is_active': True
                }
            )

            # If Sinf exists but Belgisi is different, update Belgisi
            if not created and sinf_obj.belgisi != belgisi:
                sinf_obj.belgisi = belgisi
                sinf_obj.save()
                print(f"Sinf updated with new Belgisi: {sinf_obj}")

            # Fetch courses
            courses = Kurs.objects.filter(id__in=course_ids)

        except ObjectDoesNotExist as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Xatolik: {str(e)} - Noto'g'ri ID."})

        try:
            # Create and save the SubmittedStudent object
            student = SubmittedStudent(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                sinf=sinf_obj,
                kasb=kasb,
                yonalish=yonalish,
                filial=filial,
                belgisi=belgisi.nomi,
                status='pending',
                added_by=request.user
            )
            student.save()

            # Add selected courses to the student
            student.kurslar.set(courses)  # Assign courses using the ManyToMany relationship

            print(f"Student saved with courses: {student}")
            return JsonResponse({'status': 'success', 'message': 'O\'quvchi muvaffaqiyatli qo\'shildi!'})

        except Exception as e:
            print(f"Error during student save: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Xatolik yuz berdi: {str(e)}"})

    return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri so\'rov.'})
