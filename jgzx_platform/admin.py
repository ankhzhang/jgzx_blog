from django.contrib import admin
from .models import UserProfile, Project


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'identity', 'department', 'phone')
    list_filter = ('identity',)
    search_fields = ('user__username', 'user__first_name', 'department')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'publisher', 'publisher_role', 'category', 'status', 'recruit_count', 'deadline', 'created_at')
    list_filter = ('status', 'category', 'publisher_role')
    search_fields = ('title', 'description')
    raw_id_fields = ('publisher',)
