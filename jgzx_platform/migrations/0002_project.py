# Generated manually for 项目发布模块

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jgzx_platform', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publisher_role', models.CharField(choices=[('student', '学生项目'), ('teacher', '教师项目')], max_length=10, verbose_name='发布者身份')),
                ('title', models.CharField(max_length=100, verbose_name='标题')),
                ('description', models.TextField(verbose_name='项目描述')),
                ('category', models.CharField(choices=[('research', '科研'), ('competition', '竞赛'), ('innovation', '大创项目')], max_length=20, verbose_name='类别')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('pending', '待审'), ('published', '已发布'), ('recruit_full', '已招满'), ('ended', '已结束'), ('offline', '已下架')], default='draft', max_length=20, verbose_name='状态')),
                ('recruit_count', models.PositiveSmallIntegerField(default=1, verbose_name='招募人数')),
                ('skill_requirements', models.JSONField(blank=True, default=list, verbose_name='技能要求')),
                ('deadline', models.DateTimeField(verbose_name='招募截止时间')),
                ('is_visible_when_ended', models.BooleanField(default=True, verbose_name='已结束是否对他人可见')),
                ('offline_reason', models.CharField(blank=True, max_length=500)),
                ('offline_at', models.DateTimeField(blank=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('reject_reason', models.CharField(blank=True, max_length=500, verbose_name='驳回原因')),
                ('prev_status', models.CharField(blank=True, max_length=20, verbose_name='下架前状态')),
                ('version', models.PositiveIntegerField(default=1, verbose_name='乐观锁版本')),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_projects', to=settings.AUTH_USER_MODEL)),
                ('offline_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='offlined_projects', to=settings.AUTH_USER_MODEL)),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='published_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '项目',
                'verbose_name_plural': '项目',
                'ordering': ['-created_at'],
            },
        ),
    ]
