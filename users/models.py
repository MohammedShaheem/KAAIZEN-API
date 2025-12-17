from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils import timezone
from core.models import UUIDModel,TimeStampedModel
from .choices import UserRole

class UserManager(BaseUserManager):
    def _create_user(self, email,password,**extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        if not password:
            raise ValueError("Password must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email,password,**extra_fields):
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('role',UserRole.CLIENT)
        
        return self._create_user(email,password,**extra_fields)

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('role',UserRole.ADMIN)
        
        return self._create_user(email,password,**extra_fields)

class User(AbstractBaseUser,PermissionsMixin,UUIDModel,TimeStampedModel):
    username = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(unique=True,null=False,blank=False)
    google_id = models.CharField(max_length=200,unique=True,blank=True,null=True)
    role = models.CharField(max_length=100,choices=UserRole.choices,default = UserRole.CLIENT)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True,null=True)
    
    USERNAME_FIELD = 'email'

    
    objects = UserManager()
    
    class Meta:
        verbose_name = ('User')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.email