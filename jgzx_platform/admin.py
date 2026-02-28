from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django import forms

from .models import UserProfile, Project, Comment


# ==================== 1. 内联管理 ====================

class UserProfileInline(admin.StackedInline):
    """用户资料内联编辑"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'
    fields = ('identity', 'phone', 'department', 'avatar', 'bio',
              'is_banned', 'ban_reason', 'banned_until')


# ==================== 2. 自定义 User Admin（权限提升 + 用户封禁） ====================

class UserAdmin(BaseUserAdmin):
    """自定义用户管理，支持权限提升和用户封禁"""
    inlines = (UserProfileInline,)

    # 列表显示
    list_display = ('username', 'email', 'first_name', 'is_staff',
                    'get_identity', 'get_ban_status', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__identity', 'profile__is_banned')

    # 搜索功能
    search_fields = ('username', 'first_name', 'email', 'profile__phone', 'profile__department')

    # 批量操作
    actions = ['make_staff', 'remove_staff', 'ban_users', 'unban_users']

    def get_identity(self, obj):
        """显示用户身份"""
        return obj.profile.get_identity_display() if hasattr(obj, 'profile') else '-'
    get_identity.short_description = '身份'

    def get_ban_status(self, obj):
        """显示封禁状态"""
        if hasattr(obj, 'profile') and obj.profile.is_banned:
            return format_html('<span style="color: red;">已封禁</span>')
        return format_html('<span style="color: green;">正常</span>')
    get_ban_status.short_description = '状态'

    # ===== 批量操作：权限提升 =====

    @admin.action(description='设为管理员（批量提权）')
    def make_staff(self, request, queryset):
        """将选中用户设为管理员"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'已成功将 {updated} 个用户设为管理员', messages.SUCCESS)

    @admin.action(description='取消管理员权限')
    def remove_staff(self, request, queryset):
        """取消选中用户的管理员权限"""
        # 防止取消自己的管理员权限
        queryset = queryset.exclude(id=request.user.id)
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'已成功取消 {updated} 个用户的管理员权限', messages.SUCCESS)

    # ===== 批量操作：用户封禁 =====

    @admin.action(description='封禁选中用户')
    def ban_users(self, request, queryset):
        """封禁选中用户"""
        # 防止封禁自己
        queryset = queryset.exclude(id=request.user.id)
        count = 0
        for user in queryset:
            if hasattr(user, 'profile'):
                user.profile.is_banned = True
                user.profile.ban_reason = '管理员批量封禁'
                user.profile.save()
                count += 1
        self.message_user(request, f'已成功封禁 {count} 个用户', messages.SUCCESS)

    @admin.action(description='解封选中用户')
    def unban_users(self, request, queryset):
        """解封选中用户"""
        count = 0
        for user in queryset:
            if hasattr(user, 'profile'):
                user.profile.is_banned = False
                user.profile.ban_reason = ''
                user.profile.banned_until = None
                user.profile.save()
                count += 1
        self.message_user(request, f'已成功解封 {count} 个用户', messages.SUCCESS)


# 重新注册 User 模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ==================== 3. 项目审核 Admin ====================

class ProjectReviewForm(forms.Form):
    """项目审核表单"""
    reject_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '请输入驳回理由（驳回时必填）'}),
        required=False,
        label='驳回理由'
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """项目管理后台，支持审核流"""

    # 列表显示
    list_display = ('title', 'publisher', 'status_colored', 'created_at', 'reviewed_by', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')

    # 搜索功能（全局搜索）
    search_fields = ('title', 'description', 'publisher__username', 'publisher__first_name', 'reject_reason')

    # 日期分层
    date_hierarchy = 'created_at'

    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'publisher', 'publisher_role', 'category', 'recruit_count', 'skill_requirements', 'deadline', 'is_visible_when_ended')
        }),
        ('审核信息', {
            'fields': ('status', 'reject_reason', 'reviewed_by', 'reviewed_at', 'submitted_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('下架信息', {
            'fields': ('offline_reason', 'offline_at', 'offline_by', 'prev_status'),
            'classes': ('collapse',)
        }),
    )

    # 只读字段
    readonly_fields = ('reviewed_by', 'reviewed_at', 'created_at', 'updated_at', 'submitted_at', 'published_at', 'offline_at', 'version')

    # 批量操作
    actions = ['approve_projects', 'reject_projects', 'publish_projects', 'unpublish_projects']

    # 自定义按钮
    change_list_template = 'admin/project_change_list.html'

    def status_colored(self, obj):
        """带颜色的状态显示"""
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'published': 'green',
            'recruit_full': 'blue',
            'ended': 'purple',
            'offline': 'red'
        }
        status_names = dict(Project.STATUS_CHOICES)
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            status_names.get(obj.status, obj.status)
        )
    status_colored.short_description = '审核状态'

    # ===== 一键批复操作 =====

    @admin.action(description='✅ 通过选中项目')
    def approve_projects(self, request, queryset):
        """批量通过项目"""
        count = 0
        for project in queryset.filter(status='pending'):
            project.status = 'published'
            project.reviewed_by = request.user
            project.reviewed_at = timezone.now()
            project.published_at = timezone.now()
            project.reject_reason = ''
            project.save()
            count += 1
        self.message_user(request, f'已成功通过 {count} 个项目', messages.SUCCESS)

    @admin.action(description='❌ 驳回选中项目')
    def reject_projects(self, request, queryset):
        """批量驳回项目 - 需要填写理由"""
        if 'apply' in request.POST:
            form = ProjectReviewForm(request.POST)
            if form.is_valid():
                reject_reason = form.cleaned_data['reject_reason']
                count = 0
                for project in queryset.filter(status='pending'):
                    project.status = 'draft'
                    project.reject_reason = reject_reason or '未填写理由'
                    project.reviewed_by = request.user
                    project.reviewed_at = timezone.now()
                    project.save()
                    count += 1
                self.message_user(request, f'已成功驳回 {count} 个项目', messages.SUCCESS)
                return None
        else:
            form = ProjectReviewForm()

        return render(request, 'admin/reject_confirmation.html', {
            'title': '确认驳回项目',
            'queryset': queryset,
            'form': form,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        })

    @admin.action(description='发布选中项目')
    def publish_projects(self, request, queryset):
        """批量发布项目"""
        count = 0
        for project in queryset:
            if project.status == 'published':
                continue
            project.status = 'published'
            project.published_at = timezone.now()
            project.save()
            count += 1
        self.message_user(request, f'已成功发布 {count} 个项目', messages.SUCCESS)

    @admin.action(description='下架选中项目')
    def unpublish_projects(self, request, queryset):
        """批量下架项目"""
        count = 0
        for project in queryset:
            if project.status == 'offline':
                continue
            project.prev_status = project.status
            project.status = 'offline'
            project.offline_at = timezone.now()
            project.offline_by = request.user
            project.save()
            count += 1
        self.message_user(request, f'已成功下架 {count} 个项目', messages.SUCCESS)

    # ===== 自定义 URL 和视图 =====

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pending/', self.admin_site.admin_view(self.pending_view), name='project_pending'),
        ]
        return custom_urls + urls

    def pending_view(self, request):
        """待审核项目专属视图"""
        pending_projects = Project.objects.filter(status='pending').select_related('publisher')

        context = {
            'title': '待审核项目列表',
            'pending_projects': pending_projects,
            'opts': self.model._meta,
            'has_add_permission': self.has_add_permission(request),
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/pending_projects.html', context)

    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，添加待审核快捷入口"""
        extra_context = extra_context or {}
        extra_context['pending_count'] = Project.objects.filter(status='pending').count()
        return super().changelist_view(request, extra_context=extra_context)


# ==================== 4. 评论审核 Admin ====================

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理后台，支持审核流"""

    # 列表显示
    list_display = ('short_content', 'author', 'project', 'status_colored', 'created_at')
    list_filter = ('status', 'created_at')

    # 搜索功能（全局搜索）
    search_fields = ('content', 'author__username', 'author__first_name', 'project__title')

    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('project', 'author', 'content')
        }),
        ('审核信息', {
            'fields': ('status', 'reject_reason', 'reviewed_by', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )

    # 只读字段
    readonly_fields = ('reviewed_by', 'reviewed_at', 'created_at', 'updated_at')

    # 批量操作
    actions = ['approve_comments', 'reject_comments']

    def short_content(self, obj):
        """截断显示评论内容"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = '评论内容'

    def status_colored(self, obj):
        """带颜色的状态显示"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        status_names = dict(Comment.STATUS_CHOICES)
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            status_names.get(obj.status, obj.status)
        )
    status_colored.short_description = '审核状态'

    # ===== 一键批复操作 =====

    @admin.action(description='✅ 通过选中评论')
    def approve_comments(self, request, queryset):
        """批量通过评论"""
        count = 0
        for comment in queryset.filter(status='pending'):
            comment.status = 'approved'
            comment.reviewed_by = request.user
            comment.reviewed_at = timezone.now()
            comment.save()
            count += 1
        self.message_user(request, f'已成功通过 {count} 条评论', messages.SUCCESS)

    @admin.action(description='❌ 驳回选中评论')
    def reject_comments(self, request, queryset):
        """批量驳回评论"""
        count = 0
        for comment in queryset.filter(status='pending'):
            comment.status = 'rejected'
            comment.reject_reason = '内容违规'
            comment.reviewed_by = request.user
            comment.reviewed_at = timezone.now()
            comment.save()
            count += 1
        self.message_user(request, f'已成功驳回 {count} 条评论', messages.WARNING)

    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，显示待审核数量"""
        extra_context = extra_context or {}
        extra_context['pending_count'] = Comment.objects.filter(status='pending').count()
        return super().changelist_view(request, extra_context=extra_context)


# ==================== 5. 自定义 Admin 站点配置 ====================

admin.site.site_header = '教改项目平台管理后台'
admin.site.site_title = '教改项目平台'
admin.site.index_title = '后台管理首页'
