# 项目类别改为四类：教师科研项目、学科竞赛、大创项目-创新类、大创项目-创业类

from django.db import migrations, models


def migrate_old_categories(apps, schema_editor):
    """将旧三类映射到新四类"""
    Project = apps.get_model('jgzx_platform', 'Project')
    mapping = {
        'research': 'teacher_research',
        'competition': 'subject_competition',
        'innovation': 'innovation_innov',
    }
    for old, new in mapping.items():
        Project.objects.filter(category=old).update(category=new)


class Migration(migrations.Migration):

    dependencies = [
        ('jgzx_platform', '0002_project'),
    ]

    operations = [
        migrations.RunPython(migrate_old_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.CharField(
                choices=[
                    ('teacher_research', '教师科研项目'),
                    ('subject_competition', '学科竞赛'),
                    ('innovation_innov', '大创项目-创新类'),
                    ('innovation_venture', '大创项目-创业类'),
                ],
                max_length=24,
                verbose_name='类别',
            ),
        ),
    ]
