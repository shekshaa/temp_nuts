from django import forms
from ads.models import Advertisement, Images
from django.forms import inlineformset_factory


class AdvertisementCreationForm(forms.ModelForm):
    # category1 = forms.CharField(max_length=12)
    # category2 = forms.CharField(max_length=12)
    # category3 = forms.CharField(max_length=12)

    class Meta:
        model = Advertisement
        # fields = ('title', 'price', 'description', 'city', 'is_urgent', 'category1', 'category2', 'category3')
        fields = ('title', 'price', 'description', 'state', 'city', 'is_urgent', 'category')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        if commit:
            self.instance = Advertisement.objects.create(title=self.cleaned_data['title'],
                                                         price=self.cleaned_data['price'],
                                                         is_urgent=self.cleaned_data['is_urgent'],
                                                         description=self.cleaned_data['description'],
                                                         state=self.cleaned_data['state'],
                                                         city=self.cleaned_data['city'],
                                                         category=self.cleaned_data['category'],
                                                         user=self.user)

        return self.instance


class ImagesCreationForm(forms.ModelForm):

    class Meta:
        model = Images
        exclude = ()


ImagesFormset = inlineformset_factory(parent_model=Advertisement, model=Images, fields=('image',),
                                      form=ImagesCreationForm, extra=3)
