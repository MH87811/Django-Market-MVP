from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None, **extra_fields):
        if not username or not email or not phone:
            raise ValueError('Users must have Usernames and Emails and Phones at the same time')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_vendor', True)
        # extra_fields.setdefault('is_superuser', True)
        user = self.create_user(username=username, email=email, phone=phone, password=password, **extra_fields)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Vendors
    shop_name = models.CharField(max_length=32, blank=True, null=True)
    shop_logo = models.ImageField(upload_to='logos', blank=True, null=True)
    shop_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'