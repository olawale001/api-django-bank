from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext as _

class CustomUserManager(UserManager):
    def _create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email('email')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)


    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
         
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Super must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Super must have is is_superuser=True'))
        
        return self.create_user(username, email, password, **extra_fields)
    
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, blank=True)
    username = models.CharField(max_length=150, unique=True, blank=True) 
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)   
    is_verified = models.BooleanField(_('Is verified'), default=False)

    objects = CustomUserManager()
    
    EMAIL_FIELD= 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.name or self.get_full_name()
    

class ForgetPassword(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'), on_delete=models.CASCADE)    
    otp = models.CharField(_('OTP'), max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)



