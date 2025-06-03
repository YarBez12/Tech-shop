from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("A valid email hasn't been provided")
        email = self.normalize_email(email)
        username = extra_fields.get('username', email.split('@')[0])
        user = self.model(email=email, username = username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class Address(models.Model):
    address_field1 = models.CharField(max_length=255, default='', blank=True)
    address_field2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.address_field1


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(blank=True, null=True)
    address = models.ForeignKey(Address, blank=True, null=True, on_delete=models.SET_NULL, related_name='users')
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)


    def __str__(self):
        return self.username
    

class Action(models.Model):
    user = models.ForeignKey(User,
        related_name='actions',
        on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    target_ct = models.ForeignKey(ContentType,
        blank=True,
        null=True,
        related_name='target_obj',
        on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True,
        blank=True)
    target = GenericForeignKey('target_ct', 'target_id')
    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['target_ct', 'target_id']),
        ]
        ordering = ['-created']


class NotificationState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen_news = models.DateTimeField(null=True, blank=True)
    last_seen_actions = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notification state for {self.user.email}"