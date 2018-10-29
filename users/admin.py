from django.contrib import admin
from .models import *


class UserBookmarkInline(admin.StackedInline):
    model = Bookmark
    extra = 1


class UserAdmin(admin.ModelAdmin):
    inlines = [UserBookmarkInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
