from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, View, UpdateView
from ads.forms import AdvertisementCreationForm, ImagesFormset
from django.shortcuts import get_object_or_404
from ads.models import Advertisement, Images, Category
from django.db import transaction

from users.models import Member
import math

PAGE_SIZE = 6


class HomeView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            if not hasattr(self.request.user, 'member'):
                member = Member(user=self.request.user)
                member.save()
                self.request.user.member = member

        context = super().get_context_data(**kwargs)
        context['cats'] = Category.objects.filter(level=1)
        context['max_possible_page'] = max(1, int(math.ceil(Advertisement.objects.all().count() / PAGE_SIZE)))

        return context


class AdvertisementCreationView(CreateView):
    model = Advertisement
    form_class = AdvertisementCreationForm
    success_url = '/'
    template_name = 'create_ad.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['cats'] = Category.objects.filter(level=1)

        if self.request.POST:
            data['images'] = ImagesFormset(self.request.POST, self.request.FILES)
            print(self.request.POST)
            print(self.request.FILES)
        else:
            data['images'] = ImagesFormset()

        return data

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), **{'user': self.get_object()}}

    def form_valid(self, form):
        context = self.get_context_data()
        images = context['images']

        ret = super().form_valid(form)

        with transaction.atomic():
            # self.object = form.save(commit=False)

            if images.is_valid():
                images.instance = self.object
                images.save()

        return ret

    def get_object(self, queryset=None):
        return self.request.user.member


class AdvertisementViewView(TemplateView):
    template_name = 'view_ad.html'

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advertisement_id = self.kwargs['id']
        advertisement = get_object_or_404(Advertisement, id=advertisement_id)
        context['id'] = advertisement_id
        context['title'] = advertisement.title
        context['price'] = advertisement.price
        context['description'] = advertisement.description
        context['state'] = advertisement.state
        context['city'] = advertisement.city
        context['creation_time'] = advertisement.creation_time
        context['is_urgent'] = advertisement.is_urgent
        context['category3'] = advertisement.category
        context['category2'] = advertisement.category.parent
        context['category1'] = advertisement.category.parent.parent
        context['user_phone'] = advertisement.user.phone
        context['user_email'] = advertisement.user.email
        context['sharable_link'] = 'ads/view/' + str(advertisement_id)
        context['images'] = Images.objects.filter(advertisement=advertisement_id)

        return context


class AdvertisementArchiveView(UpdateView):
    model = Advertisement
    fields = ['is_archived']
    success_url = reverse_lazy('ads:my-ads')

    def get_object(self, queryset=None):
        ret = get_object_or_404(Advertisement, id=self.request.POST['id'])
        if self.request.user.is_superuser or ret.user == self.request.user.member:
            return ret
        raise PermissionDenied()


class MyAdsView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['ads'] = []
        ads = Advertisement.objects.all()
        for ad in ads:
            images = Images.objects.filter(advertisement=ad.id)
            if len(images) != 0:
                image = images[0]
            else:
                image = ''
            if ad.user == self.request.user.member:
                context['ads'].append(
                    {'name': ad.title, 'info': ad.description, 'id': ad.id, 'image': image, 'is_archived': ad.is_archived})

        return context


class CategoryDropdownView(View):
    def get(self, request, *args, **kwargs):
        parent_id = int(request.GET.get('parent_id', 0))
        queryset = Category.objects.filter(parent_id=parent_id)
        return HttpResponse(render_to_string('cat_dd.html', {'cats': queryset}))


def search(request):
    page = request.GET.get('page', None)
    title = request.GET.get('title', None)

    category1 = request.GET.get('select1', None)
    category2 = request.GET.get('select2', None)
    category3 = request.GET.get('category', None)

    state = request.GET.get('state', None)
    city = request.GET.get('city', None)

    price_low = request.GET.get('price_low', None)
    price_high = request.GET.get('price_high', None)

    is_urgent = request.GET.get('is_urgent', None)
    is_image = request.GET.get('is_image', None)

    ads = Advertisement.objects.filter(is_archived=False)

    if title:
        ads = ads.filter(title__icontains=title)

    if state:
        ads = ads.filter(state=state.strip())
    if city and city.strip():  # in some situations, the not-selected-city was sent as a few space characters
        ads = ads.filter(city=city.strip())

    if price_low and price_high:
        ads = ads.filter(Q(price__gte=int(price_low)) & Q(price__lte=int(price_high)))
    elif price_low:
        ads = ads.filter(price__gte=int(price_low))
    elif price_high:
        ads = ads.filter(price__lte=int(price_high))

    if is_urgent:
        ads = ads.filter(is_urgent=True)
    if category3:
        ads = ads.filter(category=category3)
    elif category2:
        ads = ads.filter(category__parent=category2)
    elif category1:
        ads = ads.filter(category__parent__parent=category1)

    final_ids = []
    for ad in ads:
        if is_image is None or (len(ad.images.all()) > 0 and is_image) or (
                len(ad.images.all()) == 0 and not is_image):
            final_ids.append(ad.id)

    max_page = max(1, int(math.ceil(len(final_ids) / PAGE_SIZE)))
    if page:
        page = int(page)
        if page > max_page:
            page = max_page
        final_ads = Advertisement.objects.filter(id__in=final_ids)[(page - 1) * PAGE_SIZE:page * PAGE_SIZE]
    else:
        final_ads = Advertisement.objects.filter(id__in=final_ids)[:PAGE_SIZE]

    context = dict()

    context['max_page'] = max_page
    context['cats'] = Category.objects.filter(level=1)
    context['ads'] = []
    for ad in final_ads:
        images = Images.objects.filter(advertisement=ad.id)
        if len(images) != 0:
            image = images[0]
        else:
            image = ''
        context['ads'].append({'name': ad.title, 'info': ad.description, 'id': ad.id, 'image': image})

    return HttpResponse(render_to_string('ads_list.html', context=context))
