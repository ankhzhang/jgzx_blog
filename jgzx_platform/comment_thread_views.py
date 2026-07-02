from django.db import transaction
from django.db.models import Count
from django.db import ProgrammingError, OperationalError
from django.utils import timezone
from rest_framework import permissions, status, views
from rest_framework.response import Response

from .comment_serializers import (
    CommentCreateSerializer,
    CommentTreeItemSerializer,
    MyCommentItemSerializer,
)
from .models import Project, ProjectCommentReadState, ProjectThreadComment, CommentReplyReadState
from .project_visibility import is_project_publicly_visible


def _get_visible_project(request, pk):
    try:
        obj = Project.objects.select_related('publisher').get(pk=pk, deleted_at__isnull=True)
    except Project.DoesNotExist:
        return None
    if request.user and request.user.is_authenticated:
        if request.user.is_staff or request.user.id == obj.publisher_id:
            return obj
    if is_project_publicly_visible(obj):
        return obj
    return None


class ProjectCommentListCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, project_id):
        project = _get_visible_project(request, project_id)
        if project is None:
            return Response({'error': '项目不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)

        try:
            roots = list(
                ProjectThreadComment.objects.filter(
                    project_id=project.id, parent_id__isnull=True, is_deleted=False
                ).select_related('author').order_by('created_at')
            )
        except (ProgrammingError, OperationalError):
            return Response({'project_id': project.id, 'items': []})
        root_ids = [item.id for item in roots]
        replies = ProjectThreadComment.objects.filter(
            parent_id__in=root_ids, is_deleted=False
        ).select_related('author').order_by('created_at')
        grouped = {}
        for reply in replies:
            grouped.setdefault(reply.parent_id, []).append(reply)
        for root in roots:
            root.prefetched_replies = grouped.get(root.id, [])

        data = CommentTreeItemSerializer(roots, many=True, context={'request': request}).data
        return Response({'project_id': project.id, 'items': data})

    @transaction.atomic
    def post(self, request, project_id):
        if not request.user or not request.user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)

        project = _get_visible_project(request, project_id)
        if project is None:
            return Response({'error': '项目不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        parent_id = serializer.validated_data.get('parent_id')
        parent = None
        if parent_id is not None:
            try:
                parent = ProjectThreadComment.objects.get(
                    id=parent_id, project_id=project.id, is_deleted=False
                )
            except ProjectThreadComment.DoesNotExist:
                return Response({'error': '回复目标不存在'}, status=status.HTTP_404_NOT_FOUND)
            if parent.parent_id is not None:
                return Response({'error': '仅支持二级回复'}, status=status.HTTP_400_BAD_REQUEST)

        comment = ProjectThreadComment.objects.create(
            project=project,
            author=request.user,
            parent=parent,
            content=serializer.validated_data['content'],
        )

        if project.publisher_id != request.user.id:
            ProjectCommentReadState.objects.create(
                owner_id=project.publisher_id,
                project_id=project.id,
                comment=comment,
                is_read=False,
            )

        if parent is not None and parent.author_id != request.user.id:
            CommentReplyReadState.objects.create(
                owner_id=parent.author_id,
                comment=comment,
                is_read=False,
            )

        output = CommentTreeItemSerializer(comment, context={'request': request}).data
        return Response(output, status=status.HTTP_201_CREATED)


class ProjectCommentDeleteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def delete(self, request, comment_id):
        try:
            comment = ProjectThreadComment.objects.select_related('author').get(id=comment_id, is_deleted=False)
        except ProjectThreadComment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not (request.user.is_staff or request.user.id == comment.author_id):
            return Response({'error': '无权限删除'}, status=status.HTTP_403_FORBIDDEN)

        comment.is_deleted = True
        comment.deleted_at = timezone.now()
        comment.deleted_by = request.user
        comment.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyCommentListView(views.APIView):
    """当前用户的个人评论中心"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            my_comments = ProjectThreadComment.objects.filter(
                author=user, is_deleted=False,
            ).select_related('project', 'author', 'parent', 'parent__author').order_by('-created_at')

            replies_to_me = ProjectThreadComment.objects.filter(
                parent__author=user, is_deleted=False,
            ).exclude(author=user).select_related(
                'project', 'author', 'parent', 'parent__author',
            ).order_by('-created_at')

            project_new_comments = list(
                ProjectCommentReadState.objects.filter(
                    owner=user, is_read=False,
                ).values('project_id', 'project__title').annotate(
                    unread_count=Count('id'),
                ).order_by('-unread_count')
            )
            project_new_comments = [
                {
                    'project_id': item['project_id'],
                    'project_title': item['project__title'],
                    'unread_count': item['unread_count'],
                }
                for item in project_new_comments
            ]

            unread_project_comment_count = ProjectCommentReadState.objects.filter(
                owner=user, is_read=False,
            ).count()
            unread_reply_count = CommentReplyReadState.objects.filter(
                owner=user, is_read=False,
            ).count()
        except (ProgrammingError, OperationalError):
            return Response({
                'my_comments': [],
                'replies_to_me': [],
                'project_new_comments': [],
                'unread_project_comment_count': 0,
                'unread_reply_count': 0,
            })

        context = {'request': request}
        return Response({
            'my_comments': MyCommentItemSerializer(my_comments, many=True, context=context).data,
            'replies_to_me': MyCommentItemSerializer(replies_to_me, many=True, context=context).data,
            'project_new_comments': project_new_comments,
            'unread_project_comment_count': unread_project_comment_count,
            'unread_reply_count': unread_reply_count,
        })


class CommentRepliesMarkReadView(views.APIView):
    """将「收到的回复」全部标记为已读"""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            updated = CommentReplyReadState.objects.filter(
                owner_id=request.user.id,
                is_read=False,
            ).update(is_read=True, read_at=timezone.now())
        except (ProgrammingError, OperationalError):
            updated = 0
        return Response({'marked_count': updated})


class CommentUnreadCountView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            count = ProjectCommentReadState.objects.filter(
                owner_id=request.user.id, is_read=False
            ).count()
        except (ProgrammingError, OperationalError):
            count = 0
        return Response({'unread_count': count})


class ProjectCommentMarkReadView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, project_id):
        try:
            updated = ProjectCommentReadState.objects.filter(
                owner_id=request.user.id,
                project_id=project_id,
                is_read=False,
            ).update(is_read=True, read_at=timezone.now())
        except (ProgrammingError, OperationalError):
            updated = 0
        return Response({'marked_count': updated})
