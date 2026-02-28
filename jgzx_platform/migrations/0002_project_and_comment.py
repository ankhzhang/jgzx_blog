# Generated manually for 项目发布模块和评论模块

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
                ('category', models.CharField(choices=[('teacher_research', '教师科研项目'), ('subject_competition', '学科竞赛'), ('innovation_innov', '大创项目-创新类'), ('innovation_venture', '大创项目-创业类')], max_length=24, verbose_name='类别')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('pending', '待审'), ('published', '已发布'), ('recruit_full', '已招满'), ('ended', '已结束'), ('offline', '已下架')], default='draft', max_length=20, verbose_name='状态')),
                ('recruit_count', models.PositiveSmallIntegerField(default=1, verbose_name='招募人数')),
                ('skill_requirements', models.JSONField(blank=True, default=list, verbose_name='技能要求')),
                ('deadline', models.DateTimeField(verbose_name='招募截止时间')),
                ('is_visible_when_ended', models.BooleanField(default=True, verbose_name='已结束是否对他人可见')),
                ('offline_reason', models.CharField(blank=True, max_length=500, verbose_name='下架原因')),
                ('offline_at', models.DateTimeField(blank=True, null=True, verbose_name='下架时间')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='删除时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('submitted_at', models.DateTimeField(blank=True, null=True, verbose_name='提交审核时间')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='发布时间')),
                ('reject_reason', models.CharField(blank=True, max_length=500, verbose_name='驳回原因')),
                ('prev_status', models.CharField(blank=True, max_length=20, verbose_name='下架前状态')),
                ('version', models.PositiveIntegerField(default=1, verbose_name='乐观锁版本')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_projects', to=settings.AUTH_USER_MODEL, verbose_name='删除人')),
                ('offline_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='offlined_projects', to=settings.AUTH_USER_MODEL, verbose_name='下架人')),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='published_projects', to=settings.AUTH_USER_MODEL, verbose_name='发布者')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_projects', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '项目',
                'verbose_name_plural': '项目',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='评论内容')),
                ('status', models.CharField(choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回')], default='pending', max_length=20, verbose_name='审核状态')),
                ('reject_reason', models.TextField(blank=True, verbose_name='驳回理由')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='作者')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='jgzx_platform.project', verbose_name='所属项目')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_comments', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '评论',
                'verbose_name_plural': '评论',
                'ordering': ['-created_at'],
            },
        ),
    ]
