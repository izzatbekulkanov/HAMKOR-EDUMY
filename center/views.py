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

class CoursesView(TemplateView):

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
