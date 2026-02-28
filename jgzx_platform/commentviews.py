from django.utils import timezone
from django.db.models import Q
from rest_framework import views, status, permissions
from rest_framework.response import Response

from .models import Project, Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from .projectviews import ProjectQuerysetMixin


class ProjectCommentListCreateView(views.APIView, ProjectQuerysetMixin):
    """
    项目评论列表 & 创建
    GET: 列出某项目下的评论（树状：一级 + 二级）
    POST: 创建评论或回复
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def _get_project_or_404(self, request, pk):
        """
        与项目详情保持一致的可见性规则：
        - 公开：已发布；
        - recruit_full / ended 且 is_visible_when_ended=True；
        - 项目发布者本人或管理员。
        """
        try:
            obj = Project.objects.select_related('publisher').get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return None

        # 公开可见
        if obj.status == 'published':
            return obj
        if obj.status in ('recruit_full', 'ended') and obj.is_visible_when_ended:
            return obj
        # 本人或管理员
        if request.user and request.user.is_authenticated:
            if obj.publisher_id == request.user.id or request.user.is_staff:
                return obj
        return None

    def get(self, request, pk):
        project = self._get_project_or_404(request, pk)
        if not project:
            return Response({'error': '项目不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)

        # 仅一级评论，按时间升序；replies 通过序列化器嵌套
        queryset = (
            Comment.objects.filter(project_id=project.id, parent__isnull=True)
            .select_related('author', 'author__profile')
            .prefetch_related('replies', 'replies__author', 'replies__author__profile')
            .order_by('created_at')
        )
        serializer = CommentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            return Response({'error': '请先登录后再评论'}, status=status.HTTP_401_UNAUTHORIZED)

        # 封禁用户不可评论
        if hasattr(request.user, 'profile') and getattr(request.user.profile, 'is_banned', False):
            return Response({'error': '账号已被封禁，无法发表评论'}, status=status.HTTP_403_FORBIDDEN)

        project = self._get_project_or_404(request, pk)
        if not project:
            return Response({'error': '项目不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)

        # 仅已发布/已招满/已结束项目允许评论，且未下架
        if project.status not in ('published', 'recruit_full', 'ended'):
            return Response({'error': '仅已发布或已结束的项目允许评论'}, status=status.HTTP_400_BAD_REQUEST)
        if project.status == 'offline':
            return Response({'error': '项目已下架，无法评论'}, status=status.HTTP_400_BAD_REQUEST)

        # 简单防刷：1 分钟内同一用户在该项目下的一级评论不超过 2 条
        parent_id = request.data.get('parent')
        if not parent_id:
            one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
            count = Comment.objects.filter(
                project_id=project.id,
                author_id=request.user.id,
                parent__isnull=True,
                created_at__gte=one_minute_ago,
            ).count()
            if count >= 2:
                return Response(
                    {'error': '评论过于频繁，请稍后再试'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

        serializer = CommentCreateSerializer(
            data=request.data,
            context={'request': request, 'project': project},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()

        # 更新作者评论计数
        profile = getattr(request.user, 'profile', None)
        if profile is not None:
            profile.comment_count = (profile.comment_count or 0) + 1
            profile.save(update_fields=['comment_count'])

        output = CommentSerializer(comment, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(views.APIView):
    """
    删除评论（软删）
    - 评论作者可以删除自己的评论
    - 管理员可以删除任何评论
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.select_related('author', 'author__profile').get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'error': '评论不存在'}, status=status.HTTP_404_NOT_FOUND)

        if comment.deleted_at is not None:
            return Response({'error': '评论已删除'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not (user.is_staff or comment.author_id == user.id):
            return Response({'error': '无权限删除该评论'}, status=status.HTTP_403_FORBIDDEN)

        comment.deleted_at = timezone.now()
        comment.deleted_by = user
        comment.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])

        # 减少评论者计数（不小于 0）
        profile = getattr(comment.author, 'profile', None)
        if profile is not None and profile.comment_count > 0:
            profile.comment_count -= 1
            profile.save(update_fields=['comment_count'])

        return Response(status=status.HTTP_204_NO_CONTENT)

