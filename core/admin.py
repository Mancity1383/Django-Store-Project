from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as MainUserAdmin
from .models import User
# Register your models here.


@admin.register(User)
class UserAdmin(MainUserAdmin):
    add_fieldsets =(
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2",'email','first_name','last_name'),
            },
        ),


