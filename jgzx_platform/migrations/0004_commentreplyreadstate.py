from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jgzx_platform', '0003_userprofile_major'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentReplyReadState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='已读时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='reply_read_state', to='jgzx_platform.projectthreadcomment', verbose_name='回复评论')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_reply_read_states', to=settings.AUTH_USER_MODEL, verbose_name='被回复者')),
            ],
            options={
                'verbose_name': '回复未读状态',
                'verbose_name_plural': '回复未读状态',
                'indexes': [models.Index(fields=['owner', 'is_read'], name='jgzx_platfo_owner_i_8a1f2c_idx')],
            },
        ),
    ]
