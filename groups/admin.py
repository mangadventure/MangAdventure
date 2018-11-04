from django.contrib import admin
from .models import Role, Group, Member


class MemberRoleInline(admin.StackedInline):
    model = Role
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    inlines = [MemberRoleInline]


class GroupAdmin(admin.ModelAdmin):
    exclude = ['id']


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)

