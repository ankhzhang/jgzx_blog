# 项目发布模块 — 视图与权限
from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Project
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    RejectBodySerializer,
    OfflineBodySerializer,
    CloseRecruitBodySerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """仅项目发布者或管理员"""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return getattr(obj, 'publisher_id', None) == request.user.id


class ProjectQuerysetMixin:
    """项目列表可见性：公开=已发布或(已结束且可见)；我的=本人；管理=全部(含软删可单独参数)"""

    def get_queryset(self, request, mine=False, include_deleted=False):
        qs = Project.objects.select_related('publisher').all()
        if not include_deleted and not getattr(self, 'allow_deleted', False):
            qs = qs.filter(deleted_at__isnull=True)

        if mine:
            if not request.user or not request.user.is_authenticated:
                return Project.objects.none()
            qs = qs.filter(publisher_id=request.user.id)
            return qs

        if request.user and request.user.is_staff:
            return qs

        # 公开：published 或 (recruit_full/ended 且 is_visible_when_ended)
        qs = qs.filter(
            Q(status='published')
            | (Q(status__in=['recruit_full', 'ended']) & Q(is_visible_when_ended=True))
        )
        return qs


def _content_changed(instance, attrs):
    keys = ['title', 'description', 'category', 'recruit_count', 'skill_requirements', 'deadline']
    for k in keys:
        if k in attrs and getattr(instance, k) != attrs[k]:
            return True
    return False


# ---------- 列表 GET + 创建 POST /api/projects/ ----------
class ProjectListCreateView(views.APIView, ProjectQuerysetMixin):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        mine = request.query_params.get('mine', '').lower() in ('1', 'true', 'yes')
        category = request.query_params.get('category', '').strip()
        publisher_role = request.query_params.get('publisher_role', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        keyword = request.query_params.get('q', '').strip()
        tags_param = request.query_params.get('tags', '').strip()

        if mine:
            qs = self.get_queryset(request, mine=True)
        else:
            qs = self.get_queryset(request, mine=False)

        if category and category in dict(Project.CATEGORY_CHOICES):
            qs = qs.filter(category=category)
        if publisher_role and publisher_role in dict(Project.PUBLISHER_ROLE_CHOICES):
            qs = qs.filter(publisher_role=publisher_role)
        if status_filter and status_filter in dict(Project.STATUS_CHOICES):
            qs = qs.filter(status=status_filter)
        if keyword:
            qs = qs.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
            )
        if tags_param:
            # tags=a,b => 任意一个标签命中即返回
            raw_tags = [t.strip() for t in tags_param.split(',')]
            tag_list = [t for t in raw_tags if t]
            if tag_list:
                tag_q = Q()
                for t in tag_list:
                    tag_q |= Q(tags__contains=[t])
                qs = qs.filter(tag_q)

        qs = qs.order_by('-created_at')[:200]
        serializer = ProjectListSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        is_draft = request.data.get('is_draft', True)
        serializer = ProjectCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        role = getattr(request.user.profile, 'identity', 'student') if hasattr(request.user, 'profile') else 'student'
        if role not in ('student', 'teacher'):
            role = 'student'
        project = serializer.save(
            publisher=request.user,
            publisher_role=role,
            status='draft' if is_draft else 'pending',
            submitted_at=timezone.now() if not is_draft else None,
        )
        return Response(
            ProjectDetailSerializer(project).data,
            status=status.HTTP_201_CREATED,
        )


# ---------- 详情 ----------
class ProjectDetailView(views.APIView, ProjectQuerysetMixin):
    permission_classes = [permissions.AllowAny]

    def get_object(self, request, pk):
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
        obj = self.get_object(request, pk)
        if obj is None:
            return Response({'error': '项目不存在或无权查看'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProjectDetailSerializer(obj).data)


# ---------- 更新 ----------
class ProjectUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_object(self, request, pk):
        try:
            return Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return None

    def put(self, request, pk):
        project = self.get_object(request, pk)
        if project is None:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not (request.user.is_staff or project.publisher_id == request.user.id):
            return Response({'error': '无权限修改'}, status=status.HTTP_403_FORBIDDEN)
        if project.status not in ('draft', 'published'):
            return Response(
                {'error': '仅草稿或已发布状态可编辑正文'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        version = request.data.get('version')
        if version is not None and project.version != int(version):
            return Response(
                {'error': '数据已被修改，请刷新后重试'},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ProjectCreateUpdateSerializer(project, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        attrs = serializer.validated_data
        # 已发布且内容有变更 -> 回待审
        if project.status == 'published' and _content_changed(project, attrs):
            attrs['status'] = 'pending'
            attrs['submitted_at'] = timezone.now()
            attrs['reject_reason'] = ''
        attrs['version'] = project.version + 1
        serializer.save(**attrs)
        return Response(ProjectDetailSerializer(Project.objects.get(pk=pk)).data)


# ---------- 提交审核 ----------
class ProjectSubmitView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.publisher_id != request.user.id and not request.user.is_staff:
            return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        if project.status != 'draft':
            return Response({'error': '仅草稿可提交审核'}, status=status.HTTP_400_BAD_REQUEST)

        project.status = 'pending'
        project.submitted_at = timezone.now()
        project.reject_reason = ''
        project.version += 1
        project.save(update_fields=['status', 'submitted_at', 'reject_reason', 'version', 'updated_at'])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 撤回审核 ----------
class ProjectWithdrawView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.publisher_id != request.user.id and not request.user.is_staff:
            return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        if project.status != 'pending':
            return Response({'error': '仅待审可撤回'}, status=status.HTTP_400_BAD_REQUEST)

        project.status = 'draft'
        project.version += 1
        project.save(update_fields=['status', 'version', 'updated_at'])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 审核通过 ----------
class ProjectApproveView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.status != 'pending':
            return Response({'error': '仅待审可审核通过'}, status=status.HTTP_400_BAD_REQUEST)

        project.status = 'published'
        project.published_at = timezone.now()
        project.reject_reason = ''
        project.version += 1
        project.save(update_fields=['status', 'published_at', 'reject_reason', 'version', 'updated_at'])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 审核驳回 ----------
class ProjectRejectView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.status != 'pending':
            return Response({'error': '仅待审可驳回'}, status=status.HTTP_400_BAD_REQUEST)

        body = RejectBodySerializer(data=request.data)
        if not body.is_valid():
            return Response(body.errors, status=status.HTTP_400_BAD_REQUEST)

        project.status = 'draft'
        project.reject_reason = body.validated_data['reject_reason']
        project.version += 1
        project.save(update_fields=['status', 'reject_reason', 'version', 'updated_at'])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 关闭招募/已结束 ----------
class ProjectCloseRecruitView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.publisher_id != request.user.id and not request.user.is_staff:
            return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        if project.status not in ('published', 'recruit_full', 'ended'):
            return Response({'error': '仅已发布/已招满/已结束可操作'}, status=status.HTTP_400_BAD_REQUEST)

        body = CloseRecruitBodySerializer(data=request.data)
        if not body.is_valid():
            return Response(body.errors, status=status.HTTP_400_BAD_REQUEST)
        target = body.validated_data['target']

        project.status = target
        project.version += 1
        project.save(update_fields=['status', 'version', 'updated_at'])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 下架 ----------
class ProjectOfflineView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)

        body = OfflineBodySerializer(data=request.data)
        if not body.is_valid():
            return Response(body.errors, status=status.HTTP_400_BAD_REQUEST)

        project.prev_status = project.status
        project.status = 'offline'
        project.offline_reason = body.validated_data['offline_reason']
        project.offline_at = timezone.now()
        project.offline_by = request.user
        project.version += 1
        project.save(update_fields=[
            'prev_status', 'status', 'offline_reason', 'offline_at', 'offline_by_id',
            'version', 'updated_at',
        ])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 恢复下架 ----------
class ProjectRestoreView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.status != 'offline':
            return Response({'error': '仅已下架可恢复'}, status=status.HTTP_400_BAD_REQUEST)

        prev = project.prev_status or 'draft'
        if prev not in dict(Project.STATUS_CHOICES):
            prev = 'draft'
        project.status = prev
        project.offline_reason = ''
        project.offline_at = None
        project.offline_by = None
        project.prev_status = ''
        project.version += 1
        project.save(update_fields=[
            'status', 'offline_reason', 'offline_at', 'offline_by_id', 'prev_status',
            'version', 'updated_at',
        ])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 修改结束可见 ----------
class ProjectVisibilityView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def patch(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.publisher_id != request.user.id and not request.user.is_staff:
            return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)

        visible = request.data.get('is_visible_when_ended')
        if visible is None:
            return Response({'error': '请传 is_visible_when_ended'}, status=status.HTTP_400_BAD_REQUEST)
        project.is_visible_when_ended = bool(visible)
        project.version += 1
        project.save(update_fields=['is_visible_when_ended', 'version', 'updated_at'])
        return Response(ProjectDetailSerializer(project).data)


# ---------- 删除（软删，仅草稿） ----------
class ProjectDeleteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def delete(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, deleted_at__isnull=True)
        except Project.DoesNotExist:
            return Response({'error': '项目不存在'}, status=status.HTTP_404_NOT_FOUND)
        if project.publisher_id != request.user.id and not request.user.is_staff:
            return Response({'error': '无权限'}, status=status.HTTP_403_FORBIDDEN)
        if project.status != 'draft':
            return Response({'error': '仅草稿可删除'}, status=status.HTTP_400_BAD_REQUEST)

        project.deleted_at = timezone.now()
        project.deleted_by = request.user
        project.save(update_fields=['deleted_at', 'deleted_by_id', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)
