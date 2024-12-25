from django.contrib.auth.mixins import LoginRequiredMixin
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
