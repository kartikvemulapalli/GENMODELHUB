from djongo import models
from django.contrib.auth.models import BaseUserManager, Group, Permission
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a name")
        
        user = self.model(email=self.normalize_email(email), name=name, password=password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(models.Model):  # No AbstractBaseUser
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)  
    password = models.CharField(max_length=255)  # Plain text password
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name="customuser_set",
        related_query_name="user",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  

    def __str__(self):
        return self.email

    def check_password(self, raw_password):
        """Custom check_password method for plain text passwords (Not secure)."""
        return self.password == raw_password  # Direct comparison (for testing only)

    @property
    def is_authenticated(self):
        return True  # Any logged-in user is authenticated

    @property
    def is_anonymous(self):
        return False  # Custom users are never anonymous


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.name  
