from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

PHONE_NUMBER_REGEX = RegexValidator(
    r'^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$', 'invalid phone number')
class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('provider', 'Solution Provider'),
        ('seeker', 'Solution Seeker'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    otp = models.CharField(max_length=6, null=True, blank=True)  # Add the otp field here
    class Meta:
        # db_table = 'CustomUser'
        ordering = ('pk',)

    def is_group_member(self, group_name):
            return self.groups.filter(name=group_name).exists()

    @property
    def is_admin(self):
        return self.is_group_member('admin')

    @property
    def is_provider_user(self):
        return self.is_group_member('provider')

    @property
    def is_seeker_user(self):
        return self.is_group_member('seeker')

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone_number = models.TextField(
        max_length=20, blank=True, null=True, validators=[PHONE_NUMBER_REGEX])
