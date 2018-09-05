from django.contrib import admin
from .models import *


class MemberRoleInline(admin.StackedInline):
    model = Role
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    inlines = [MemberRoleInline]


admin.site.register(Group)
admin.site.register(Member, MemberAdmin)
