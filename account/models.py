from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
# Create your models here.


class AccountManager(BaseUserManager):
    def create_user(self, name, userName, email, number, password=None,):
        if not name:
            raise ValueError("user must have a Name")
        if not userName:
            raise ValueError("Users must have an username")
        user = self.model(
            name=name,
            userName=userName,
        )
        # user.profile_pic = photoUrl
        user.number = number
        if email is None:
            user.email = email
        else:
            user.email = self.normalize_email(email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, userName, email, number, password):
        user = self.create_user(
            name=name,
            userName=userName,
            password=password,
            email=email,
            number=number
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Account(AbstractBaseUser):
    name = models.CharField(max_length=150, blank=False)
    userName = models.CharField(max_length=70, unique=True, blank=False)
    number = models.CharField(max_length=30, unique=True, null=True, blank=True,)
    email = models.EmailField(max_length=500, blank=False, null=True)
    profile_pic = models.ImageField(upload_to='profile_img/', null=True, blank=True, )
    date_joined = models.DateTimeField(verbose_name='date-joined', auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_youtuber = models.BooleanField(default=False)

    USERNAME_FIELD ='userName'
    # EMAIL_FIELD ='email'
    REQUIRED_FIELDS = ['email', 'name', 'number']

    objects = AccountManager()

    def __str__(self):
        return self.userName

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Otpveification1(models.Model):
    number = models.CharField(max_length=30, blank=False,)
    otp = models.IntegerField(blank=True,)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
