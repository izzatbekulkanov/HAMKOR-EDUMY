from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, UpdateView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from account.models import CustomUser
from center.models import Center, Filial, Images
from web_project import TemplateLayout
from django.utils.decorators import method_decorator
from django.urls import reverse


class CenterView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Center modelining barcha ma'lumotlarini olish
        centers = Center.objects.all()

        # Ma'lumotlarni context ga qo'shish
        context['centers'] = centers

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
