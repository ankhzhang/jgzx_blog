from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
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
