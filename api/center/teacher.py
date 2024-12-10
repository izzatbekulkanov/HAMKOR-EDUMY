from django.http import JsonResponse
from center.models import SubmittedStudent, Sinf, Kasb, Yonalish, Filial
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from school.models import Belgisi, Maktab
import json


@csrf_exempt
@login_required  # Bu funksiyani faqat tizimga kirgan foydalanuvchi bajarishi mumkin
def submit_student(request):
    if request.method == 'POST':
        # JSON formatidagi ma'lumotlarni olish
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Ma\'lumotlar formatida xatolik.'})

        # Form ma'lumotlarini olingan JSONdan ajratib oling
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone')  # Telefon raqami
        sinf = data.get('grade')  # 'sinf' emas, balki 'grade' bo'lishi kerak
        kasb_id = data.get('profession')
        yonalish_id = data.get('field')
        belgisi_name = data.get('section')
        filial_id = data.get('branch')  # 'filial' emas, balki 'branch' bo'lishi kerak

        # Debug: Print extracted form data
        print(f"Received data: first_name={first_name}, last_name={last_name}, phone_number={phone_number}, sinf={sinf}, kasb_id={kasb_id}, yonalish_id={yonalish_id}, belgisi_name={belgisi_name}, filial_id={filial_id}")

        # Check if all required fields are provided
        if not all([first_name, last_name, phone_number, sinf, kasb_id, yonalish_id, belgisi_name, filial_id]):
            print("Error: Not all required fields are provided.")
            return JsonResponse({'status': 'error', 'message': 'Barcha maydonlarni to\'ldiring!'})

        # Fix sinf format (only the first number before " - " is considered)
        sinf = sinf.split(' - ')[0]  # Only the first part before " - " is taken
        print(f"Corrected sinf value: {sinf}")

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

            # Get related objects using the IDs
            sinf_obj = Sinf.objects.filter(sinf_raqami=sinf).first()
            print(f"Found Sinf: {sinf_obj}")

            if not sinf_obj:
                # If Sinf doesn't exist, create a new one with the provided data
                maktab = Maktab.objects.get(id=data.get('school'))  # Assuming school ID is passed as well
                print(f"Found Maktab: {maktab}")

                belgisi = Belgisi.objects.filter(nomi=belgisi_name).first()
                print(f"Found Belgisi: {belgisi}")

                if not belgisi:
                    # Create new Belgisi if it doesn't exist
                    belgisi = Belgisi.objects.create(nomi=belgisi_name)
                    print(f"Created new Belgisi: {belgisi}")

                # Create new Sinf if it doesn't exist
                sinf_obj = Sinf.objects.create(
                    maktab=maktab,
                    sinf_raqami=sinf,
                    belgisi=belgisi
                )
                print(f"Created new Sinf: {sinf_obj}")
            else:
                # If Sinf exists, ensure Belgisi is set correctly
                belgisi = sinf_obj.belgisi or Belgisi.objects.create(nomi=belgisi_name)
                print(f"Using existing Belgisi: {belgisi}")

            # Fetch Kasb, Yonalish, and Filial objects
            kasb = Kasb.objects.get(id=kasb_id)
            print(f"Found Kasb: {kasb}")

            yonalish = Yonalish.objects.get(id=yonalish_id)
            print(f"Found Yonalish: {yonalish}")

            filial = Filial.objects.get(id=filial_id)  # Get the Filial by ID
            print(f"Found Filial: {filial}")

        except ObjectDoesNotExist as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Xatolik: {str(e)} - Noto'g'ri ID."})

        try:
            # Create and save the SubmittedStudent object with phone number
            student = SubmittedStudent(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,  # Saving the phone number
                sinf=sinf_obj,
                kasb=kasb,
                yonalish=yonalish,
                filial=filial,  # Assign the Filial to the student
                belgisi=belgisi.nomi,  # Store the name of Belgisi
                status='pending',  # default status
                added_by=request.user  # Link the current logged-in user to the 'added_by' field
            )
            student.save()
            print(f"Student saved: {student}")

            return JsonResponse({'status': 'success', 'message': 'O\'quvchi muvaffaqiyatli qo\'shildi!'})

        except Exception as e:
            print(f"Error during student save: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f"Xatolik yuz berdi: {str(e)}"})

    return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri so\'rov.'})
