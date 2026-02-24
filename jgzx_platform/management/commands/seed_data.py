import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from jgzx_platform.models import UserProfile, Project, Comment


class Command(BaseCommand):
    help = '生成测试数据：用户、项目和评论'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='要创建的用户数量（默认10）'
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=20,
            help='要创建的项目数量（默认20）'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=50,
            help='要创建的评论数量（默认50）'
        )

    def handle(self, *args, **options):
        user_count = options['users']
        project_count = options['projects']
        comment_count = options['comments']

        self.stdout.write(self.style.SUCCESS('开始生成测试数据...'))

        with transaction.atomic():
            # 1. 创建测试用户
            users = self.create_users(user_count)
            self.stdout.write(self.style.SUCCESS(f'✓ 创建了 {len(users)} 个用户'))

            # 2. 创建项目
            projects = self.create_projects(projects=project_count, users=users)
            self.stdout.write(self.style.SUCCESS(f'✓ 创建了 {len(projects)} 个项目'))

            # 3. 创建评论
            comments = self.create_comments(comments=comment_count, projects=projects, users=users)
            self.stdout.write(self.style.SUCCESS(f'✓ 创建了 {len(comments)} 条评论'))

        self.stdout.write(self.style.SUCCESS('\n🎉 测试数据生成完成！'))
        self.stdout.write(self.style.NOTICE('\n数据统计：'))
        self.stdout.write(f'  - 用户总数: {User.objects.count()}')
        self.stdout.write(f'  - 项目总数: {Project.objects.count()}')
        self.stdout.write(f'  - 评论总数: {Comment.objects.count()}')
        self.stdout.write(self.style.NOTICE('\n审核状态统计：'))
        for status, name in Project.STATUS_CHOICES:
            count = Project.objects.filter(status=status).count()
            self.stdout.write(f'  - 项目「{name}」: {count}')
        for status, name in Comment.STATUS_CHOICES:
            count = Comment.objects.filter(status=status).count()
            self.stdout.write(f'  - 评论「{name}」: {count}')

    def create_users(self, count):
        """创建测试用户"""
        users = []
        departments = ['计算机学院', '软件学院', '信息学院', '电子工程学院', '自动化学院']
        identities = ['student', 'teacher']
        
        # 检查是否已存在测试用户
        existing_count = User.objects.filter(username__startswith='test_').count()
        
        for i in range(existing_count + 1, existing_count + count + 1):
            username = f'test_{i:03d}'
            email = f'test_{i:03d}@example.com'
            identity = random.choice(identities)
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password='test123456',
                first_name=f'测试用户{i}'
            )
            
            # 更新用户资料
            profile = user.profile
            profile.identity = identity
            profile.phone = f'138{random.randint(10000000, 99999999)}'
            profile.department = random.choice(departments)
            profile.bio = f'这是测试用户{i}的个人简介，用于测试教改项目平台功能。'
            profile.save()
            
            users.append(user)
        
        return users

    def create_projects(self, projects, users):
        """创建测试项目"""
        projects_list = []
        
        # 项目标题模板
        title_templates = [
            '基于{tech}的{target}教学改革研究',
            '{target}课程{method}教学模式探索',
            '面向{target}的{tech}应用实践',
            '{method}在{target}教学中的应用研究',
            '基于{tech}的{target}创新实验平台建设',
            '{target}课程思政教学改革与实践',
            '新工科背景下{target}课程体系优化研究',
            '{method}驱动的{target}教学改革',
        ]
        
        tech_words = ['人工智能', '大数据', '云计算', '物联网', '虚拟现实', '区块链', '5G技术']
        target_words = ['Python程序设计', '数据结构', '软件工程', '数据库原理', '计算机网络', 
                       '操作系统', '编译原理', '计算机组成原理', '算法分析', 'Web开发']
        method_words = ['项目式学习', '翻转课堂', '混合式教学', '案例教学', '问题导向', 
                       '协作学习', '探究式学习', '游戏化教学']
        
        # 项目内容模板
        content_templates = [
            '''## 项目背景

随着{tech}技术的快速发展，传统{target}教学模式已难以满足新时代人才培养需求。
本项目旨在探索{method}在{target}教学中的创新应用。

## 研究目标

1. 构建基于{tech}的{target}教学资源库
2. 设计{method}教学方案并实施
3. 建立多元化课程评价体系

## 预期成果

- 发表教改论文2-3篇
- 建设在线课程1门
- 形成可推广的教学案例集

## 创新点

将{tech}与{target}教学深度融合，突破传统教学时空限制，提升学生学习兴趣和实践能力。''',
            
            '''## 一、项目简介

本项目针对{target}课程教学中存在的{problem}问题，提出基于{method}的解决方案。

## 二、主要工作

### 1. 教学资源建设
- 开发{tech}辅助教学工具
- 编写案例教材和实验指导书
- 建设在线学习平台

### 2. 教学方法改革
- 引入{method}教学模式
- 实施小班化研讨教学
- 开展项目驱动式学习

### 3. 评价方式创新
- 过程性评价与终结性评价相结合
- 引入同行评议机制
- 建立学习档案袋

## 三、实施计划

| 阶段 | 时间 | 主要任务 |
|------|------|----------|
| 第一阶段 | 第1-3月 | 调研与方案设计 |
| 第二阶段 | 第4-9月 | 教学实施与数据收集 |
| 第三阶段 | 第10-12月 | 总结与成果提炼 |

## 四、经费预算

总预算：5万元
- 资料费：1万元
- 设备费：2万元
- 差旅费：1万元
- 其他：1万元''',
        ]
        
        problems = ['理论与实践脱节', '学生学习积极性不高', '考核方式单一', '教学资源陈旧']
        
        statuses = ['pending', 'approved', 'rejected']
        status_weights = [0.4, 0.5, 0.1]  # 40%待审核, 50%已通过, 10%已驳回
        
        for i in range(projects):
            author = random.choice(users)
            
            # 生成标题
            template = random.choice(title_templates)
            title = template.format(
                tech=random.choice(tech_words),
                target=random.choice(target_words),
                method=random.choice(method_words)
            )
            
            # 生成内容
            content_template = random.choice(content_templates)
            content = content_template.format(
                tech=random.choice(tech_words),
                target=random.choice(target_words),
                method=random.choice(method_words),
                problem=random.choice(problems)
            )
            
            # 随机状态
            status = random.choices(statuses, weights=status_weights)[0]
            
            project = Project.objects.create(
                title=title,
                content=content,
                author=author,
                status=status,
                is_published=(status == 'approved'),
                view_count=random.randint(0, 1000)
            )
            
            # 如果已审核，添加审核信息
            if status in ['approved', 'rejected']:
                admin_users = User.objects.filter(is_staff=True)
                if admin_users.exists():
                    project.reviewed_by = random.choice(admin_users)
                    project.reviewed_at = datetime.now() - timedelta(days=random.randint(1, 30))
                    if status == 'rejected':
                        project.reject_reason = random.choice([
                            '研究内容不够具体，需要补充详细实施方案',
                            '与现有项目重复度较高，建议调整研究方向',
                            '经费预算不合理，请重新核算',
                            '缺少前期研究基础，建议先进行预研'
                        ])
                    project.save()
            
            projects_list.append(project)
        
        return projects_list

    def create_comments(self, comments, projects, users):
        """创建测试评论"""
        comments_list = []
        
        comment_templates = [
            '这个项目很有意义，{adj}！',
            '建议增加{content}方面的内容。',
            '研究方法很新颖，值得借鉴。',
            '期待看到最终成果！',
            '已经在我们学院试点应用，效果{adj}。',
            '希望能开源相关教学资源。',
            '经费预算是否合理？建议再细化一下。',
            '项目周期是否足够完成所有目标？',
            '这个方向很有前景，支持！',
            '希望能多分享一些实施过程中的经验。',
            '学生反馈如何？有数据支撑吗？',
            '与行业需求结合紧密，实用性强。',
            '建议增加企业导师参与环节。',
            '考核方式设计得很科学，学习了。',
            '希望能组织线上研讨会交流经验。',
        ]
        
        adj_words = ['非常棒', '很好', '不错', '有待改进', '令人期待']
        content_words = ['实践案例', '数据分析', '对比实验', '学生作品', '教学视频']
        
        statuses = ['pending', 'approved', 'rejected']
        status_weights = [0.3, 0.65, 0.05]  # 30%待审核, 65%已通过, 5%已驳回
        
        for i in range(comments):
            project = random.choice(projects)
            author = random.choice(users)
            
            # 确保评论者不是项目作者（也可以允许，这里随机）
            if random.random() > 0.3:
                author = random.choice([u for u in users if u != project.author] or users)
            
            # 生成评论内容
            template = random.choice(comment_templates)
            content = template.format(
                adj=random.choice(adj_words),
                content=random.choice(content_words)
            )
            
            # 随机状态
            status = random.choices(statuses, weights=status_weights)[0]
            
            comment = Comment.objects.create(
                project=project,
                author=author,
                content=content,
                status=status
            )
            
            # 如果已审核，添加审核信息
            if status in ['approved', 'rejected']:
                admin_users = User.objects.filter(is_staff=True)
                if admin_users.exists():
                    comment.reviewed_by = random.choice(admin_users)
                    comment.reviewed_at = datetime.now() - timedelta(days=random.randint(1, 30))
                    if status == 'rejected':
                        comment.reject_reason = random.choice([
                            '包含不当言论',
                            '与项目无关',
                            '涉及敏感信息'
                        ])
                    comment.save()
            
            comments_list.append(comment)
        
        return comments_list
