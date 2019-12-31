from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models.deletion import CASCADE

# from ads.models import Advertisement


class Member(models.Model):
    MemberType = (
        ('S', 'seller'),
        ('B', 'buyer')
    )
    user = models.OneToOneField(to=User, on_delete=CASCADE, related_name='member')
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=30)
    type = models.CharField(max_length=1, choices=MemberType)

    def __str__(self):
        return self.user.username

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def is_active(self):
        return self.user.is_active

    def save(self, *args, **kwargs):
        self.user.save()
        super().save(*args, **kwargs)


class ActivationCode(models.Model):
    member = models.ForeignKey(to=Member, related_name='activation_codes', on_delete=CASCADE)
    code = models.CharField(max_length=10)
