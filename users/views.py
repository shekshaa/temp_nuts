from .models import Member
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, CreateView, UpdateView

from users.models import Member
from ads.models import Advertisement, Images
from .forms import MemberActivationForm, BuyerCreationForm, SellerCreationForm


class MemberActivationView(FormView):
    form_class = MemberActivationForm
    success_url = '/'
    template_name = 'activation.html'

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), **{'user': self.get_object()}}

    def get_object(self):
        return get_object_or_404(Member, user__username=self.kwargs['username'])


class SellerCreationView(CreateView):
    form_class = SellerCreationForm
    template_name = 'seller_signup.html'

    def get_success_url(self):
        return reverse('users:activation', args=[self.request.POST['username']])


class BuyerCreationView(CreateView):
    form_class = BuyerCreationForm
    template_name = 'buyer_signup.html'

    def get_success_url(self):
        return reverse('users:activation', args=[self.request.POST['username']])

class EditProfileView(UpdateView):
    model = Member
    fields = ['phone', 'address']
    template_name = 'edit_profile.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user.member
