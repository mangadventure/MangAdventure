from django.contrib.auth.models import Group
from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    exclude = ['password', 'groups']


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)

