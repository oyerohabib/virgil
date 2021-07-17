from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .constants import Actions
import datetime
import pytz
from django.db.models.signals import post_save
from django.dispatch import receiver
import json
from django.urls import reverse
from .renderers import *



class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = datetime.datetime.now(pytz.utc)
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        user_type.objects.update_or_create(
            user=user,
            defaults={
                'is_admin': True
            }
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # CUSTOM USER FIELDS
    firstname = models.CharField(max_length=30, blank=True, null=True)
    lastname = models.CharField(max_length=30, blank=True, null=True)
    telephone = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=300)
    zipcode = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    region = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    additional_address = models.CharField(max_length=30, blank=True, null=True)
    picture = models.ImageField(upload_to='images/users', blank=True, null=True, default='images/users/profile-pixs.jpg')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
        
    def get_email(self):
        return self.email
        
    def get_fullname(self):
        return str(self.firstname) + " " + str(self.lastname)

    def get_picture_url(self):
        if self.picture and hasattr(self.picture, 'url'):
            return self.picture.url
        else:
            return "/media/images/users/profile-pixs.jpg"

class user_type(models.Model):
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.is_manager == True:
            return User.get_email(self.user) + " - is_manager"
        else:
            return User.get_email(self.user) + " - is_admin"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='notifications')
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name=_('content type'),
        blank=True,
        null=True
    )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    action = models.PositiveSmallIntegerField(_('action'), choices=Actions.CHOICES)
    text = models.TextField(_('text'), blank=True)
    date = models.DateTimeField(_('date'), auto_now_add=True)
    is_seen = models.BooleanField(_('seen status'), default=False)
    is_read = models.BooleanField(_('read status'), default=False)

    __data = None

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        db_table = 'station_notifications'

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('notification_detail', kwargs={'pk': self.pk})

    @property
    def data(self):
        if self.__data is None:
            self.__data = json.loads(self.text)
        return self.__data

    def render(self):
        renderers = {
            Actions.STATION_COMPLETED: render_station,
            Actions.TRANSACTION_COMPLETED: render_transaction
        }
        renderer_function = renderers[self.action]
        return renderer_function(self)

class Station(models.Model):

    STATION_STATUS = (
            ("pending", "pending"),
            # ("declined", "declined"),
            ("active", "active"),
            ("blocked", "blocked")
        )

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    zipcode = models.IntegerField()
    city = models.CharField(max_length=20)
    region = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    ipaddress = models.CharField(max_length=20)
    macaddress = models.CharField(max_length=20)
    # cigarettecounter = models.IntegerField()
    status = models.CharField(default="pending", choices=STATION_STATUS, max_length=10)

    def __str__(self):
        return self.name

class Transaction(models.Model):

    TRANSACTION_STATUS = (
            ("pending", "pending"),
            ("declined", "declined"),
            ("modify", "modify"),
            ("completed", "completed")
        )

    cigarettecounter = models.IntegerField()
    price = models.FloatField()
    videolink = models.URLField()
    status = models.CharField(default="pending" ,choices=TRANSACTION_STATUS, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Transaction" + str(self.id)  + " by " + str(self.user)

    @property    
    def get_detail(self):
        return "Transaction" + str(self.id)  + " by " + str(self.user)

    @property    
    def get_picture_url(self):
        return self.user.picture.url

    @property    
    def get_user_email(self):
        return self.user.email

class Error(models.Model):

    ERROR_CHOICE = (
            ("unsolved", "unsolved"),
            ("solved", "solved"),
        )

    code = models.CharField(max_length=10)
    description = models.TextField()
    status = models.CharField(default="unsolved", choices=ERROR_CHOICE, max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.CharField(max_length=40)
    file = models.FileField(upload_to="files/error")

    def __str__(self):
        return "Error " + self.code + " from " + str(self.station)

class Solution(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    error = models.ForeignKey(Error, on_delete=models.CASCADE)

    def __str__(self):
        return "Solution for " + str(self.error) + " by " + str(self.user)

class Message(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Message Sent by " + str(self.user_id)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
            instance.profile.save()