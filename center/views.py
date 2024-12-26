from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
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
        school_ids = SubmittedStudent.objects.filter(sinf__maktab__isnull=False).values_list('sinf__maktab', flat=True).distinct()
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