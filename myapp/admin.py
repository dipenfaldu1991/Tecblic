from django.contrib import admin

# Register your models here.
from .models import CustomUser,UserProfile



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UsernameField




class UserCreationForm(BaseUserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
        )
        field_classes = {'username': UsernameField}



admin.site.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'middle_name', 'last_name', 'email', 'mobile_phone')}),
        ('Permissions', {
            'fields': ('is_active', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    add_form = UserCreationForm
    list_display = ('id', 'username', 'email', 'first_name', 'middle_name', 'last_name', 'is_staff')
    list_display_links = ('id', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'middle_name', 'last_name', 'email')
    ordering = ('username',)


admin.site.register(UserProfile)