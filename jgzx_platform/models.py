from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    IDENTITY_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
    )

    # 与django自带的User表关联
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # 业务身份
    identity = models.CharField('身份标签', max_length=10, choices=IDENTITY_CHOICES, default='student')
    # 基础信息
    phone = models.CharField('联系电话', max_length=15, blank=True)
    department = models.CharField('部门', max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 状态字段（封禁功能预留，此版本暂不做）
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    banned_until = models.DateTimeField(null=True, blank=True)

    # 统计字段（统计功能预留，可暂不做）
    project_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f"{self.user.username}-{self.identity}"


# 信号部分，确保User一创建，Profile就会存在
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# 信号部分，确保User有更新时，同步Profile
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ---------- 项目发布模块 ----------
class Project(models.Model):
    """项目主表：学生/教师发布的项目，含状态流转与审核"""

    PUBLISHER_ROLE_CHOICES = (
        ('student', '学生项目'),
        ('teacher', '教师项目'),
    )
    CATEGORY_CHOICES = (
        ('teacher_research', '教师科研项目'),
        ('subject_competition', '学科竞赛'),
        ('innovation_innov', '大创项目-创新类'),
        ('innovation_venture', '大创项目-创业类'),
    )
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('pending', '待审'),
        ('published', '已发布'),
        ('recruit_full', '已招满'),
        ('ended', '已结束'),
        ('offline', '已下架'),
    )

    publisher = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='published_projects'
    )
    publisher_role = models.CharField(
        '发布者身份', max_length=10, choices=PUBLISHER_ROLE_CHOICES
    )
    title = models.CharField('标题', max_length=100)
    description = models.TextField('项目描述')
    category = models.CharField('类别', max_length=24, choices=CATEGORY_CHOICES)
    status = models.CharField(
        '状态', max_length=20, choices=STATUS_CHOICES, default='draft'
    )
    recruit_count = models.PositiveSmallIntegerField('招募人数', default=1)
    skill_requirements = models.JSONField('技能要求', default=list, blank=True)
    tags = models.JSONField('标签', default=list, blank=True)
    deadline = models.DateTimeField('招募截止时间')
    is_visible_when_ended = models.BooleanField(
        '已结束是否对他人可见', default=True
    )

    offline_reason = models.CharField(
        '下架原因', max_length=500, blank=True
    )
    offline_at = models.DateTimeField(null=True, blank=True)
    offline_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='offlined_projects'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='deleted_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.CharField(
        '驳回原因', max_length=500, blank=True
    )
    prev_status = models.CharField(
        '下架前状态', max_length=20, blank=True
    )
    version = models.PositiveIntegerField('乐观锁版本', default=1)

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'


class Comment(models.Model):
    """项目评论：一级评论 + 二级回复（树状最多两层）"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='comments', verbose_name='所属项目'
    )
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='comments', verbose_name='评论者'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='父评论',
    )
    content = models.TextField('评论内容')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deleted_comments',
        verbose_name='删除人',
    )

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'Comment({self.id}) on {self.project_id}'
