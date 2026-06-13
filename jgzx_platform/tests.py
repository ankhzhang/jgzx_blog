from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, ProjectCommentReadState, ProjectThreadComment


class CommentThreadTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pwd12345', first_name='负责人')
        self.student = User.objects.create_user(username='stu', password='pwd12345', first_name='学生A')
        self.admin = User.objects.create_user(
            username='admin', password='pwd12345', first_name='管理员', is_staff=True
        )
        self.other = User.objects.create_user(username='other', password='pwd12345', first_name='路人')

        self.project = Project.objects.create(
            publisher=self.owner,
            publisher_role='teacher',
            title='测试项目',
            description='x' * 120,
            category='teacher_research',
            status='published',
            recruit_count=3,
            skill_requirements=['python'],
            tags=['AI'],
            deadline=timezone.now() + timedelta(days=7),
        )

    def test_create_comment_and_reply_with_unread_state(self):
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            f'/api/projects/{self.project.id}/comments/',
            {'content': '我想申请，擅长Python'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        root_id = res.data['id']

        unread = ProjectCommentReadState.objects.filter(
            owner_id=self.owner.id, project_id=self.project.id, is_read=False
        ).count()
        self.assertEqual(unread, 1)

        reply_res = self.client.post(
            f'/api/projects/{self.project.id}/comments/',
            {'content': '补充说明：有竞赛经历', 'parent_id': root_id},
            format='json',
        )
        self.assertEqual(reply_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reply_res.data['parent_id'], root_id)

    def test_third_level_reply_is_rejected(self):
        root = ProjectThreadComment.objects.create(
            project=self.project, author=self.student, content='一级'
        )
        second = ProjectThreadComment.objects.create(
            project=self.project, author=self.owner, content='二级', parent=root
        )
        self.client.force_authenticate(user=self.student)
        res = self.client.post(
            f'/api/projects/{self.project.id}/comments/',
            {'content': '三级', 'parent_id': second.id},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_permission(self):
        comment = ProjectThreadComment.objects.create(
            project=self.project, author=self.student, content='可删除评论'
        )

        self.client.force_authenticate(user=self.other)
        res_forbidden = self.client.delete(f'/api/comments/{comment.id}/delete/')
        self.assertEqual(res_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.delete(f'/api/comments/{comment.id}/delete/')
        self.assertEqual(res_admin.status_code, status.HTTP_204_NO_CONTENT)
        comment.refresh_from_db()
        self.assertTrue(comment.is_deleted)

    def test_unread_count_and_mark_read(self):
        ProjectThreadComment.objects.create(
            project=self.project, author=self.student, content='咨询内容'
        )
        read_state = ProjectCommentReadState.objects.create(
            owner=self.owner,
            project=self.project,
            comment=ProjectThreadComment.objects.create(
                project=self.project, author=self.student, content='第二条'
            ),
            is_read=False,
        )

        self.client.force_authenticate(user=self.owner)
        unread_res = self.client.get('/api/comments/unread-count/')
        self.assertEqual(unread_res.status_code, status.HTTP_200_OK)
        self.assertEqual(unread_res.data['unread_count'], 1)

        mark_res = self.client.post(f'/api/projects/{self.project.id}/comments/mark-read/')
        self.assertEqual(mark_res.status_code, status.HTTP_200_OK)
        self.assertEqual(mark_res.data['marked_count'], 1)

        read_state.refresh_from_db()
        self.assertTrue(read_state.is_read)
