import json
from collections import defaultdict

from django.utils.formats import number_format

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, UpdateView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from account.models import CustomUser
from center.models import Center, Filial, Images, SubmittedStudent, Kasb, Yonalish, Kurs, E_groups
from school.models import Sinf, Maktab
from web_project import TemplateLayout
from django.utils.decorators import method_decorator
from django.urls import reverse


class CenterView(TemplateView):
    def get_context_data(self, **kwargs):
        # Initialize the base context using TemplateLayout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchi obyektini olish
        user = self.request.user

        # Center obyektlari
        centers = Center.objects.all()

        # Userga tegishli submitted students
        submitted_students = (
            SubmittedStudent.objects.filter(added_by=user)
            if user.is_authenticated
            else SubmittedStudent.objects.none()
        )

        # Barcha submitted students
        all_submitted_students = SubmittedStudent.objects.all()

        # Faqat SubmittedStudent orqali mavjud maktablarni olish
        school_ids = SubmittedStudent.objects.filter(sinf__maktab__isnull=False).values_list('sinf__maktab',
                                                                                             flat=True).distinct()
        schools = Maktab.objects.filter(id__in=school_ids)

        # Qo'shimcha kerakli contextlar
        teachers = CustomUser.objects.filter(now_role="2")  # O'qituvchilar
        sinflar = Sinf.objects.all()  # Sinflar
        kasblar = Kasb.objects.all()  # Kasblar
        yonalishlar = Yonalish.objects.all()  # Yo'nalishlar

        # Add data to context
        context.update({
            'centers': centers,
            'grades': range(1, 12),  # 1-dan 11-gacha
            'submitted_students': submitted_students,  # Userga tegishli
            'all_submitted_students': all_submitted_students,  # Barcha submitted students
            'teachers': teachers,  # O'qituvchilar
            'schools': schools,  # Filterlangan maktablar
            'sinflar': sinflar,  # Sinflar
            'kasblar': kasblar,  # Kasblar
            'yonalishlar': yonalishlar,  # Yo'nalishlar
        })

        return context


class CenterDetailView(LoginRequiredMixin, DetailView):
    model = Center
    context_object_name = "center"
    template_name = "center_detail.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Filiallar
        context["filials"] = Filial.objects.filter(center=self.object)

        # Kasblar
        context["kasblar"] = Kasb.objects.filter(center=self.object)

        # Yo'nalishlar
        context["yonalishlar"] = Yonalish.objects.filter(center=self.object)

        # Kurslar
        context["kurslar"] = Kurs.objects.filter(center=self.object)

        # E-guruhlar
        context["e_groups"] = E_groups.objects.filter(kurs__center=self.object)

        # Yuborilgan o'quvchilar
        context["submitted_students"] = SubmittedStudent.objects.filter(filial__center=self.object)

        # Maktablar
        context[
            "maktablar"] = self.object.maktab.all()  # Center bilan ManyToManyField orqali bog'langan barcha maktablar

        # Sinflar
        sinf_list = Sinf.objects.filter(maktab__in=self.object.maktab.all())
        context["sinflar"] = sinf_list

        return context


@method_decorator(login_required, name='dispatch')
class FilialDetailUpdateView(DetailView, UpdateView):
    model = Filial
    template_name = 'fillial_details.html'
    context_object_name = 'filial'
    fields = ['location', 'contact', 'telegram', 'image', 'admins']

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['admins'] = CustomUser.objects.filter(now_role=4, added_by=self.request.user)
        return context

    def form_valid(self, form):
        with transaction.atomic():
            filial = form.save(commit=False)
            admins = self.request.POST.getlist('admins')
            filial.admins.set(CustomUser.objects.filter(id__in=admins))

            # Main image save
            if 'image' in self.request.FILES:
                filial.image = self.request.FILES['image']
            filial.save()

            # Additional images handling
            additional_images = self.request.FILES.getlist('additional_images')
            image_titles = self.request.POST.getlist('image_titles[]')
            image_descriptions = self.request.POST.getlist('image_descriptions[]')

            for i, img in enumerate(additional_images):
                title = image_titles[i] if i < len(image_titles) else "Rasm"
                description = image_descriptions[i] if i < len(image_descriptions) else ""
                image_instance = Images.objects.create(
                    image=img, title=title, description=description, user=self.request.user
                )
                filial.images.add(image_instance)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('filial-detail', kwargs={'pk': self.object.pk})


class OccupationsView(TemplateView):

    def get_context_data(self, **kwargs):
        """
        Sahifa uchun ma'lumotlarni kontekstga qo'shish.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchini olish
        user = self.request.user

        # Foydalanuvchiga biriktirilgan center (rahbari)
        rahbar_center = Center.objects.filter(rahbari=user).first()

        # Foydalanuvchi admin sifatida biriktirilgan filialga tegishli centerlarni olish
        filial_centers = Center.objects.filter(filial__admins=user).distinct()

        # Markazlarni birlashtirish (rahbar markaz + filial markazlari)
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'kasblar': [],
            })
            return context

        # Qidiruv parametri
        search_query = self.request.GET.get('q', '').strip()

        # Kasblarni olish (barcha markazlarga tegishli)
        if search_query:
            kasblar = Kasb.objects.filter(center__in=centers, nomi__icontains=search_query)
        else:
            kasblar = Kasb.objects.filter(center__in=centers)

        kasblar = kasblar.order_by('-created_at')

        # Ma'lumotlarni formatlash
        kasblar_data = []
        for kasb in kasblar:
            yonalish_count = kasb.yonalishlar.count()
            kurs_count = sum(yonalish.kurslar.count() for yonalish in kasb.yonalishlar.all())
            guruh_count = sum(
                kurs.groups.count() for yonalish in kasb.yonalishlar.all() for kurs in yonalish.kurslar.all()
            )
            kasblar_data.append({
                "id": kasb.id,
                "nomi": kasb.nomi,
                "created_at": kasb.created_at,
                "updated_at": kasb.updated_at,
                "is_active": kasb.is_active,
                "yonalish_count": yonalish_count,
                "kurs_count": kurs_count,
                "guruh_count": guruh_count,
            })

        context.update({
            'kasblar': kasblar_data,
            'search_query': search_query,
        })

        return context

    def post(self, request, *args, **kwargs):
        """
        POST so'rov: Foydalanuvchiga biriktirilgan markazga yangi `Kasb` qo'shadi.
        """
        print(f"POST so'rov qabul qilindi. Foydalanuvchi: {request.user}")

        nomi = request.POST.get("nomi")
        if not nomi:
            print("Nomi kiritilmagan.")
            return HttpResponseRedirect(f"{request.path}?status=error&message=Kasb%20nomi%20kiritilishi%20kerak.")

        center = Center.objects.filter(rahbari=request.user).first()
        if not center:
            print("Foydalanuvchiga biriktirilmagan markazga urinish.")
            return HttpResponseRedirect(
                f"{request.path}?status=error&message=Sizga%20biriktirilgan%20markaz%20mavjud%20emas.")

        try:
            # Mavjud nomni tekshirish
            if Kasb.objects.filter(nomi__iexact=nomi, center=center).exists():
                print(f"'{nomi}' nomli kasb allaqachon mavjud.")
                return HttpResponseRedirect(
                    f"{request.path}?status=error&message='{nomi}'%20nomli%20kasb%20allaqachon%20mavjud.")

            # Yangi Kasb yaratish
            kasb = Kasb.objects.create(nomi=nomi, center=center, is_active=True)
            print(f"Yaratilgan Kasb: {kasb}")
            return HttpResponseRedirect(
                f"{request.path}?status=success&message='{kasb.nomi}'%20kasbi%20muvaffaqiyatli%20qo'shildi.")
        except Exception as e:
            print(f"POST so'rovda xato: {e}")
            return HttpResponseRedirect(f"{request.path}?status=error&message=Xatolik%20yuz%20berdi:%20{str(e)}")

    def delete(self, request, *args, **kwargs):
        """
        DELETE so'rov: Foydalanuvchiga biriktirilgan markazdagi `Kasb`ni o'chiradi.
        """
        kasb_id = kwargs.get('pk')  # URL orqali kelgan kasb ID

        try:
            kasb = Kasb.objects.get(id=kasb_id)

            # Kasbga yo'nalish birikkanligini tekshirish
            if kasb.yonalishlar.exists():
                return JsonResponse(
                    {"success": False, "message": "Ushbu kasbga yo'nalishlar birikkan, o'chirib bo'lmaydi."},
                    status=400)

            # Foydalanuvchining markazlariga tegishli ekanligini tekshirish
            user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                filial__admins=request.user)
            if kasb.center not in user_centers:
                return JsonResponse({"success": False, "message": "Siz ushbu kasbni o'chirishga ruxsatga ega emassiz."},
                                    status=403)

            kasb.delete()
            return JsonResponse({"success": True, "message": "Kasb muvaffaqiyatli o'chirildi."})

        except Kasb.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kasb topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class OccupationsDetailView(DetailView):
    model = Kasb
    context_object_name = "kasb"

    def get_object(self):
        return get_object_or_404(Kasb, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        kasb = self.get_object()

        # Get all `Yonlishlar` associated with this `Kasb`
        yonalishlar = kasb.yonalishlar.all().order_by('-created_at')
        yonalishlar_data = []
        for yonalish in yonalishlar:
            kurslar = yonalish.kurslar.all()
            guruhlar_count = sum(kurs.groups.count() for kurs in kurslar)
            yonalishlar_data.append({
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "kurs_count": kurslar.count(),
                "guruh_count": guruhlar_count,
                "created_at": yonalish.created_at,
                "updated_at": yonalish.updated_at,
            })

        # Get all Yonalishlar that are not associated with this Kasb
        all_yonalishlar = Yonalish.objects.all()
        birikmagan_yonalishlar = all_yonalishlar.exclude(id__in=yonalishlar.values_list('id', flat=True))

        birikmagan_yonalishlar_data = []
        for yonalish in birikmagan_yonalishlar:
            # Kurslar va guruhlar sonini hisoblash
            kurslar = yonalish.kurslar.all()
            guruhlar_count = sum(kurs.groups.count() for kurs in kurslar)

            # Birikkan yoki birikmagan holatini aniqlash
            if yonalish.kasb:
                status = {
                    "type": "birikkan",
                    "kasb_nomi": yonalish.kasb.nomi,
                }
            else:
                status = {
                    "type": "birikmagan",
                    "kasb_nomi": None,
                }

            # Ma'lumotlarni yig'ish
            birikmagan_yonalishlar_data.append({
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "kurs_count": kurslar.count(),
                "guruh_count": guruhlar_count,
                "created_at": yonalish.created_at,
                "updated_at": yonalish.updated_at,
                "status": status,
            })

        context['yonalishlar'] = yonalishlar_data
        context['yonalishlar_count'] = len(yonalishlar_data)
        context['birikmagan_yonalishlar'] = birikmagan_yonalishlar_data
        context['birikmagan_yonalishlar_count'] = len(birikmagan_yonalishlar_data)
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        kasb = get_object_or_404(Kasb, pk=kwargs['pk'])
        yonalish_id = request.POST.get('yonalish_id')

        try:
            yonalish = Yonalish.objects.get(pk=yonalish_id)

            # Tekshirish: Yo'nalish boshqa kasbga birikkanmi?
            if yonalish.kasb and yonalish.kasb != kasb:
                return JsonResponse({
                    "success": False,
                    "message": f"'{yonalish.nomi}' yo'nalishi boshqa kasbga birikkan."
                }, status=400)

            # Yo'nalishni olib tashlash yoki qo'shish
            if yonalish.kasb == kasb:
                # Yo'nalishni kasbdan olib tashlash
                yonalish.kasb = None
                yonalish.save()
                message = "Yo'nalish muvaffaqiyatli olib tashlandi."
            else:
                # Yo'nalishni kasbga qo'shish
                yonalish.kasb = kasb
                yonalish.save()
                message = "Yo'nalish muvaffaqiyatli qo'shildi."

            return JsonResponse({"success": True, "message": message})

        except Yonalish.DoesNotExist:
            return JsonResponse({"success": False, "message": "Yo'nalish topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class LinesView(TemplateView):

    def get_context_data(self, **kwargs):
        """
        Sahifa uchun yo'nalishlar haqidagi ma'lumotlarni kontekstga qo'shish.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchini olish
        user = self.request.user

        # Foydalanuvchiga biriktirilgan markazlar
        rahbar_center = Center.objects.filter(rahbari=user).first()
        filial_centers = Center.objects.filter(filial__admins=user).distinct()
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'yonalishlar': [],
            })
            return context

        # Qidiruv parametri
        search_query = self.request.GET.get('q', '').strip()

        # Yo'nalishlarni olish
        if search_query:
            yonalishlar = Yonalish.objects.filter(
                center__in=centers,
                nomi__icontains=search_query
            )
        else:
            yonalishlar = Yonalish.objects.filter(center__in=centers)

        yonalishlar = yonalishlar.order_by('-created_at')

        # Ma'lumotlarni formatlash
        yonalishlar_data = []
        for yonalish in yonalishlar:
            kurs_count = yonalish.kurslar.count()
            guruh_count = sum(kurs.groups.count() for kurs in yonalish.kurslar.all())
            yonalishlar_data.append({
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "created_at": yonalish.created_at,
                "updated_at": yonalish.updated_at,
                "is_active": yonalish.is_active,
                "kurs_count": kurs_count,
                "guruh_count": guruh_count,
            })

        context.update({
            'yonalishlar': yonalishlar_data,
            'search_query': search_query,
        })

        return context

    def post(self, request, *args, **kwargs):
        """
        POST so'rov: yangi yo'nalish qo'shadi.
        """
        # Foydalanuvchi kiritgan ma'lumotlarni olish
        nomi = request.POST.get("nomi", "").strip()
        user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(filial__admins=request.user)

        # Foydalanuvchiga tegishli markazlarni olish
        if not nomi:
            return JsonResponse({"success": False, "message": "Yo'nalish nomi kiritilishi kerak."}, status=400)

        if not user_centers.exists():
            return JsonResponse({"success": False, "message": "Sizga tegishli markaz topilmadi yoki ruxsat yo'q."},
                                status=403)

        try:
            # Markazni tanlash (faqat bitta markazni tanlang)
            center = user_centers.first()
            print(f"Tegishli markaz: {center}")

            # Yo'nalish mavjudligini tekshirish
            if Yonalish.objects.filter(nomi__iexact=nomi, center=center).exists():
                return JsonResponse({"success": False, "message": f"'{nomi}' nomli yo'nalish allaqachon mavjud."},
                                    status=400)

            # Yangi yo'nalish yaratish
            yonalish = Yonalish.objects.create(nomi=nomi, center=center, is_active=True)
            return JsonResponse({"success": True, "message": f"'{yonalish.nomi}' yo'nalishi muvaffaqiyatli qo'shildi."})

        except Exception as e:
            # Noma'lum xatoliklarni qaytarish
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    def delete(self, request, *args, **kwargs):
        """
        DELETE so'rov: yo'nalishni o'chiradi.
        """
        yonalish_id = kwargs.get('pk')

        try:
            yonalish = Yonalish.objects.get(id=yonalish_id)

            # Yo'nalishga kurslar birikkanligini tekshirish
            if yonalish.kurslar.exists():
                return JsonResponse(
                    {"success": False, "message": "Ushbu yo'nalishga kurslar birikkan, o'chirib bo'lmaydi."},
                    status=400
                )

            # Foydalanuvchining markazlariga tegishli ekanligini tekshirish
            user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                filial__admins=request.user
            )
            if yonalish.center not in user_centers:
                return JsonResponse(
                    {"success": False, "message": "Siz ushbu yo'nalishni o'chirishga ruxsatga ega emassiz."},
                    status=403
                )

            yonalish.delete()
            return JsonResponse({"success": True, "message": "Yo'nalish muvaffaqiyatli o'chirildi."})

        except Yonalish.DoesNotExist:
            return JsonResponse({"success": False, "message": "Yo'nalish topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class LinesDetailView(DetailView):
    model = Yonalish
    context_object_name = "yonalish"

    def get_object(self):
        """
        Returns the specific Yonalish object based on the primary key in the URL.
        """
        return get_object_or_404(Yonalish, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        Prepares the context data for the template with detailed information about the Yonalish.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        yonalish = self.get_object()  # The specific Yonalish object

        # Fetch all related Kurs objects
        birikkan_kurslar = yonalish.kurslar.all()
        birikkan_kurslar_data = []
        for kurs in birikkan_kurslar:
            # Count active groups and students in the course
            groups = kurs.groups.all()
            group_count = groups.count()
            student_count = sum(group.students.count() for group in groups)

            birikkan_kurslar_data.append({
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "group_count": group_count,
                "student_count": student_count,
                "created_at": kurs.created_at,
                "updated_at": kurs.updated_at,
            })

        # Fetch all unassociated Kurs objects
        all_kurslar = Kurs.objects.filter(center=yonalish.center)
        birikmagan_kurslar = all_kurslar.exclude(id__in=birikkan_kurslar.values_list('id', flat=True))
        birikmagan_kurslar_data = []
        for kurs in birikmagan_kurslar:
            birikmagan_kurslar_data.append({
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "created_at": kurs.created_at,
                "updated_at": kurs.updated_at,
            })

        # Fetch all submitted students for the yonalish
        submitted_students = SubmittedStudent.objects.filter(yonalish=yonalish)
        submitted_students_data = []
        for student in submitted_students:
            submitted_students_data.append({
                "id": student.id,
                "full_name": f"{student.first_name} {student.last_name}",
                "phone_number": student.phone_number,
                "status": student.get_status_display(),
                "created_at": student.created_at,
                "updated_at": student.updated_at,
            })

        # Add data to the context
        context.update({
            "yonalish": yonalish,
            "birikkan_kurslar": birikkan_kurslar_data,
            "birikkan_kurslar_count": birikkan_kurslar.count(),
            "birikmagan_kurslar": birikmagan_kurslar_data,
            "birikmagan_kurslar_count": birikmagan_kurslar.count(),
            "submitted_students": submitted_students_data,
            "submitted_students_count": submitted_students.count(),
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the addition or removal of a course from the Yonalish.
        Optimized for performance and security.
        """
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Validate and extract the course ID
            kurs_id = data.get("kurs_id")
            if not kurs_id:
                return JsonResponse({"success": False, "message": "Kurs ID yuborilishi kerak."}, status=400)

            # Fetch the related Yonalish object
            yonalish = self.get_object()

            # Validate the Kurs exists and belongs to the same center as the Yonalish
            kurs = get_object_or_404(Kurs, id=kurs_id, center=yonalish.center)

            # Check if the Kurs is already associated with the Yonalish
            if yonalish.kurslar.filter(id=kurs_id).exists():
                # Remove the Kurs from the Yonalish
                yonalish.kurslar.remove(kurs)
                return JsonResponse({"success": True, "message": f"'{kurs.nomi}' kursi yo'nalishdan olib tashlandi."})
            else:
                # Add the Kurs to the Yonalish
                yonalish.kurslar.add(kurs)
                return JsonResponse({"success": True, "message": f"'{kurs.nomi}' kursi yo'nalishga qo'shildi."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "JSON formatida noto'g'ri ma'lumot yuborildi."},
                                status=400)
        except Kurs.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kurs topilmadi yoki ruxsat yo'q."}, status=404)
        except Exception as e:
            # Log exception (optional) and return a generic error
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class CoursesView(TemplateView):

    def get_context_data(self, **kwargs):
        """
        Prepares context data for the template with detailed information about courses.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get the current user
        user = self.request.user

        # Fetch centers associated with the user (as a leader or admin)
        user_centers = Center.objects.filter(rahbari=user) | Center.objects.filter(filial__admins=user)

        if not user_centers.exists():
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'kurslar': [],
            })
            return context

        # Search query for filtering courses
        search_query = self.request.GET.get('q', '').strip()

        # Fetch courses associated with the centers
        kurslar = Kurs.objects.filter(center__in=user_centers)
        if search_query:
            kurslar = kurslar.filter(nomi__icontains=search_query)

        kurslar = kurslar.order_by('-created_at')

        # Format course data for the context
        kurslar_data = []
        for kurs in kurslar:
            # Calculate group and student counts for each course
            groups = kurs.groups.all()
            group_count = groups.count()
            student_count = sum(group.students.count() for group in groups)

            # Add formatted price
            narxi_formatted = number_format(kurs.narxi, use_l10n=True, force_grouping=True)

            kurslar_data.append({
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "narxi_formatted": narxi_formatted,
                "group_count": group_count,
                "student_count": student_count,
                "created_at": kurs.created_at,
                "updated_at": kurs.updated_at,
                "is_active": kurs.is_active,
            })

        # Update context with course data and search query
        context.update({
            'kurslar': kurslar_data,
            'kurslar_count': kurslar.count(),
            'search_query': search_query,
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the creation of a new course with validation.
        """
        nomi = request.POST.get("nomi", "").strip()
        narxi = request.POST.get("narxi", "").strip()

        if not nomi:
            return JsonResponse({"success": False, "message": "Kurs nomi kiritilishi kerak."}, status=400)
        if not narxi or not narxi.isdigit() or int(narxi) <= 0:
            return JsonResponse({"success": False, "message": "Kurs narxi to'g'ri kiritilishi kerak."}, status=400)

        try:
            user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                filial__admins=request.user)

            if not user_centers.exists():
                return JsonResponse({"success": False, "message": "Sizga biriktirilgan markaz mavjud emas."},
                                    status=403)

            center = user_centers.first()
            normalized_nomi = nomi[0].upper() + nomi[1:].lower()

            if Kurs.objects.filter(center=center, nomi__iexact=normalized_nomi).exists():
                return JsonResponse({"success": False, "message": f"'{normalized_nomi}' nomli kurs allaqachon mavjud."},
                                    status=400)

            kurs = Kurs.objects.create(
                center=center,
                nomi=normalized_nomi,
                narxi=int(narxi),
                is_active=True
            )

            return JsonResponse({"success": True, "message": f"'{kurs.nomi}' kursi muvaffaqiyatli qo'shildi."})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    def delete(self, request, *args, **kwargs):
        """
        Handles the deletion of a course.
        """
        kurs_id = kwargs.get("pk")
        try:
            # Get the course object associated with the current user
            kurs = get_object_or_404(
                Kurs,
                id=kurs_id,
                center__in=Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                    filial__admins=request.user)
            )

            # Check if the course is associated with any groups
            if kurs.groups.exists():
                return JsonResponse(
                    {"success": False, "message": "Ushbu kursga guruhlar birikkan, o'chirib bo'lmaydi."}, status=400)

            # Check if the course is associated with any Yonalish
            if kurs.yonalishlar.exists():
                yonalish_names = ", ".join(yonalish.nomi for yonalish in kurs.yonalishlar.all())
                return JsonResponse(
                    {"success": False,
                     "message": f"Ushbu kurs quyidagi yo'nalish(lar)ga birikkan: {yonalish_names}. O'chirib bo'lmaydi."},
                    status=400
                )

            # If no associations exist, delete the course
            kurs.delete()
            return JsonResponse({"success": True, "message": "Kurs muvaffaqiyatli o'chirildi."})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    def patch(self, request, *args, **kwargs):
        """
        Handles the editing of a course.
        """
        kurs_id = kwargs.get("pk")
        try:
            data = json.loads(request.body)
            nomi = data.get("nomi", "").strip()
            narxi = data.get("narxi", "").strip()

            if not nomi or not narxi:
                return JsonResponse({"success": False, "message": "Kurs nomi va narxi kiritilishi kerak."}, status=400)
            if not narxi.isdigit() or int(narxi) <= 0:
                return JsonResponse({"success": False, "message": "Kurs narxi to'g'ri kiritilishi kerak."}, status=400)

            kurs = get_object_or_404(Kurs, id=kurs_id,
                                     center__in=Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                                         filial__admins=request.user))

            kurs.nomi = nomi[0].upper() + nomi[1:].lower()
            kurs.narxi = int(narxi)
            kurs.save()

            return JsonResponse({"success": True, "message": "Kurs muvaffaqiyatli tahrirlandi."})

        except Kurs.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kurs topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class LearningGroupView(TemplateView):
    template_name = "learning_groups.html"

    def get_context_data(self, **kwargs):
        """
        Prepares the context data for groups and courses associated with the user.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get the current user
        user = self.request.user

        # Fetch centers associated with the user (as a leader or admin)
        rahbar_center = Center.objects.filter(rahbari=user).first()
        filial_centers = Center.objects.filter(filial__admins=user).distinct()
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'guruhlar': [],
                'kurslar': [],
                'statistics': {},
                'days_of_week': [],
            })
            return context

        # Fetch groups and courses associated with the centers
        groups = E_groups.objects.filter(center__in=centers).order_by('-created_at')
        kurslar = Kurs.objects.filter(center__in=centers).order_by('nomi')

        # Format course data for the dropdown
        kurslar_data = [{"id": kurs.id, "nomi": kurs.nomi} for kurs in kurslar]

        # Initialize statistics
        total_groups = groups.count()
        active_groups = groups.filter(is_active=True).count()
        inactive_groups = total_groups - active_groups
        linked_groups = groups.filter(kurs__isnull=False).count()
        unlinked_groups = total_groups - linked_groups
        total_students = sum(group.students.count() for group in groups)

        # Format group data for the table
        groups_data = []
        for group in groups:
            students_count = group.students.count()
            kurs_name = group.kurs.nomi if group.kurs else "Biriktirilmagan"
            kurs_id = group.kurs.id if group.kurs else None
            groups_data.append({
                "id": group.id,
                "group_name": group.group_name,
                "kurs_name": kurs_name,
                "kurs_id": kurs_id,
                "students_count": students_count,
                "days_of_week": group.days_of_week,  # JSON massiv sifatida uzatish
                "created_at": group.created_at,
                "updated_at": group.updated_at,
                "is_active": group.is_active,
            })

        # Add days of week mapping
        days_of_week = E_groups.DAYS_OF_WEEK

        # Add all data to the context
        context.update({
            'guruhlar': groups_data,
            'kurslar': kurslar_data,
            'guruhlar_count': total_groups,
            'days_of_week': days_of_week,  # Full week days list
            'statistics': {
                'total_groups': total_groups,
                'active_groups': active_groups,
                'inactive_groups': inactive_groups,
                'linked_groups': linked_groups,
                'unlinked_groups': unlinked_groups,
                'total_students': total_students,
            },
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the creation of a new group with validation.
        """
        try:
            data = json.loads(request.body)

            group_name = data.get('group_name', '').strip()
            kurs_id = data.get('kurs')
            days_of_week = data.get('days_of_week', [])

            # Validate inputs
            if not group_name:
                return JsonResponse({"success": False, "message": "Guruh nomi kiritilishi kerak."}, status=400)
            if not kurs_id:
                return JsonResponse({"success": False, "message": "Kursni tanlang."}, status=400)
            if not days_of_week:
                return JsonResponse({"success": False, "message": "Dars kunlarini tanlang."}, status=400)

            # Get the course
            kurs = Kurs.objects.filter(id=kurs_id, center__rahbari=request.user) | \
                   Kurs.objects.filter(id=kurs_id, center__filial__admins=request.user)
            kurs = kurs.first()
            if not kurs:
                return JsonResponse({"success": False, "message": "Tanlangan kurs mavjud emas yoki ruxsat yo'q."},
                                    status=403)

            # Check if the group already exists
            if E_groups.objects.filter(group_name__iexact=group_name, kurs=kurs).exists():
                return JsonResponse({"success": False, "message": "Bunday nomdagi guruh allaqachon mavjud."},
                                    status=400)

            # Create the new group
            new_group = E_groups.objects.create(
                group_name=group_name,
                kurs=kurs,
                days_of_week=days_of_week,
                center=kurs.center
            )

            return JsonResponse(
                {"success": True, "message": f"'{new_group.group_name}' guruh muvaffaqiyatli qo'shildi."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Yaroqli ma'lumot yuborilmadi."}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        try:
            group_id = kwargs.get('pk')
            print(f"[DEBUG] Group ID: {group_id}")

            group = E_groups.objects.get(id=group_id)
            print(f"[DEBUG] Retrieved Group: {group}")

            data = json.loads(request.body)
            print(f"[DEBUG] Received Data: {data}")

            group_name = data.get('group_name', '').strip()
            kurs_id = data.get('kurs')

            print(f"[DEBUG] Parsed Data - Group Name: {group_name}, Kurs ID: {kurs_id}")

            if not group_name or not kurs_id:
                print("[DEBUG] Missing required fields")
                return JsonResponse({"success": False, "message": "Barcha maydonlar to'ldirilishi shart."}, status=400)

            kurs = Kurs.objects.filter(id=kurs_id, center=group.center).first()
            if not kurs:
                print("[DEBUG] Kurs not found or unauthorized access")
                return JsonResponse({"success": False, "message": "Kurs topilmadi yoki ruxsat yo'q."}, status=403)

            # Yangi tanlangan kunlar asosida yangilash
            group.group_name = group_name
            group.kurs = kurs
            group.save()

            print(f"[DEBUG] Group Updated Successfully: {group}")
            return JsonResponse({"success": True, "message": f"Guruh '{group.group_name}' muvaffaqiyatli yangilandi."})

        except E_groups.DoesNotExist:
            print("[DEBUG] Group not found")
            return JsonResponse({"success": False, "message": "Guruh topilmadi."}, status=404)
        except Exception as e:
            print(f"[DEBUG] Exception Occurred: {str(e)}")
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            group_id = kwargs.get('pk')  # URL dan guruh ID sini olish
            print(f"[DEBUG] Delete Group ID: {group_id}")

            group = E_groups.objects.get(id=group_id)  # Guruhni topish
            print(f"[DEBUG] Retrieved Group for Deletion: {group}")

            # Guruhda o‘quvchilar borligini tekshirish
            if group.students.exists():
                print("[DEBUG] Group has students. Deletion denied.")
                return JsonResponse(
                    {"success": False, "message": "Guruhga o'quvchilar biriktirilganligi sababli o'chirib bo'lmaydi."},
                    status=400)

            # Guruhni o‘chirish
            group.delete()

            print(f"[DEBUG] Group Deleted Successfully: {group_id}")
            return JsonResponse({"success": True, "message": f"Guruh muvaffaqiyatli o'chirildi."})

        except E_groups.DoesNotExist:
            print("[DEBUG] Group not found")
            return JsonResponse({"success": False, "message": "Guruh topilmadi."}, status=404)

        except Exception as e:
            print(f"[DEBUG] Exception Occurred: {str(e)}")
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


@csrf_exempt
def add_or_remove_day(request, group_id):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            day = data.get('day')

            if not day:
                return JsonResponse({'success': False, 'message': 'Hafta kuni ko\'rsatilmagan.'}, status=400)

            group = E_groups.objects.get(id=group_id)

            if day in group.days_of_week:
                group.days_of_week.remove(day)
                action = 'guruhdan olib tashlandi'
            else:
                group.days_of_week.append(day)
                action = 'guruhga qo\'shildi'

            group.save()

            return JsonResponse({
                'success': True,
                'message': f"'{day}' hafta kuni  {action} ."
            })

        except E_groups.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Guruh topilmadi.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Xatolik yuz berdi: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'message': 'Faoliyat turi noto\'g\'ri.'}, status=405)



class TeacherView(TemplateView):

    def get_context_data(self, **kwargs):
        # Initialize the base context using TemplateLayout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Viloyat, Tuman va Maktabni guruhlash
        viloyatlar = defaultdict(lambda: defaultdict(list))
        maktablar = Maktab.objects.filter(is_active=True)
        for maktab in maktablar:
            viloyatlar[maktab.viloyat][maktab.tuman].append({
                'id': maktab.id,
                'nomi': maktab.nomi,
                'maktab_raqami': maktab.maktab_raqami
            })

        # Markaz va Filiallarni guruhlash
        centers_data = []
        centers = Center.objects.filter(is_active=True)
        for center in centers:
            filials = center.filial_set.filter(is_active=True).values('id', 'location', 'contact')
            centers_data.append({
                'id': center.id,
                'nomi': center.nomi,
                'rahbari': center.rahbari.get_full_name() if center.rahbari else None,
                'filials': list(filials),
            })

        # Kasb, Yo'nalish va Kurslarni guruhlash
        kasb_data = []
        kasblar = Kasb.objects.filter(is_active=True)
        for kasb in kasblar:
            yonalish_data = []
            yonalishlar = kasb.yonalishlar.filter(is_active=True)
            for yonalish in yonalishlar:
                kurslar = yonalish.kurslar.filter(is_active=True).values('id', 'nomi', 'narxi')
                yonalish_data.append({
                    'id': yonalish.id,
                    'nomi': yonalish.nomi,
                    'kurslar': list(kurslar),
                })
            kasb_data.append({
                'id': kasb.id,
                'nomi': kasb.nomi,
                'yonalishlar': yonalish_data,
            })

        # Sinf va Belgilar
        sinflar = Sinf.objects.filter(is_active=True).select_related('maktab', 'belgisi')
        sinflar_data = []
        for sinf in sinflar:
            sinflar_data.append({
                'id': sinf.id,
                'sinf_raqami': sinf.sinf_raqami,
                'belgisi': sinf.belgisi.nomi if sinf.belgisi else None,
                'maktab': sinf.maktab.nomi if sinf.maktab else None,
            })

        # Context ma'lumotlarini yangilash
        context.update({
            'viloyatlar': dict(viloyatlar),
            'centers': centers_data,
            'kasblar': kasb_data,
            'sinflar': sinflar_data,
            'grades': range(1, 12),  # 1-dan 11-gacha sinflar
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            # Foydalanuvchi tomonidan yuborilgan ma'lumotlarni olish
            data = json.loads(request.body)

            # Zarur maydonlarni olish
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            phone_number = data.get('phone_number', '').strip()
            sinf_id = data.get('sinf')
            kasb_id = data.get('kasb')
            yonalish_id = data.get('yonalish')
            kurs_ids = data.get('kurslar', [])
            belgisi = data.get('belgisi', '').strip()

            # Zarur ma'lumotlarni tekshirish
            if not first_name or not last_name or not phone_number:
                return JsonResponse({"success": False, "message": "Ism, familiya va telefon raqami kiritilishi shart."}, status=400)

            # Sinf, kasb va yo'nalishlarni topish
            sinf = Sinf.objects.filter(id=sinf_id).first()
            kasb = Kasb.objects.filter(id=kasb_id).first()
            yonalish = Yonalish.objects.filter(id=yonalish_id).first()
            kurslar = Kurs.objects.filter(id__in=kurs_ids)

            # Yangi SubmittedStudent yaratish
            submitted_student = SubmittedStudent.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                sinf=sinf,
                kasb=kasb,
                yonalish=yonalish,
                belgisi=belgisi,
                added_by=request.user
            )

            # Kurslarni bog'lash
            if kurslar.exists():
                submitted_student.kurslar.set(kurslar)

            return JsonResponse({"success": True, "message": "Talaba muvaffaqiyatli qo'shildi."}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Yaroqli JSON yuborilmadi."}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)
