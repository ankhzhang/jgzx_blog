from rest_framework import views, status, permissions, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import UserProfile
from .serializers import (
    UserRegisterSerializer,
    BulkUserRegisterSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)


class RegisterView(views.APIView):
    """学生自主注册"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 注册后直接生成 Token 实现自动登录
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user.profile).data,
                'token': token.key,
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkRegisterView(views.APIView):
    """批量注册（仅限管理员，用于导入教师或学生）"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = BulkUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(views.APIView):

    """用户登录"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')  # 这里的 username 对应学号/工号
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': '请提供账号和密码'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': '账号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

        # 检查用户是否被封禁（UserProfile中定义的逻辑）
        if user.profile.is_banned:
            return Response({
                'error': '账号已被封禁',
                'reason': user.profile.ban_reason
            }, status=status.HTTP_403_FORBIDDEN)

        # 登录成功，清理并重新生成 Token
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)

        login(request, user)
        return Response({
            'user': UserProfileSerializer(user.profile).data,
            'token': token.key,
            'message': '登录成功'
        })


class LogoutView(views.APIView):
    """用户登出"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        # 彻底清除 session
        request.session.flush()
        # 设置 session 过期时间为 2 小时（7200秒）
        request.session.set_expiry(7200)
        return Response({'message': '登出成功'})


class UserProfileView(views.APIView):
    """个人资料管理"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """获取当前登录用户资料"""
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)

    def put(self, request):
        """更新个人资料（联系方式、简介等）"""
        # 使用 partial=True 允许只修改部分字段
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'user': UserProfileSerializer(request.user.profile).data,
                'message': '个人资料更新成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(views.APIView):
    """个人修改密码"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            # 修改密码后作废所有 Token，要求重新登录
            Token.objects.filter(user=user).delete()
            return Response({'message': '密码修改成功，请使用新密码重新登录'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(views.APIView):
    """用户列表（仅管理员）"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        search = request.query_params.get('search', '')

        # 使用 select_related 优化查询性能，一次性联表查出 User 信息
        profiles = UserProfile.objects.select_related('user').all()

        if search:
            profiles = profiles.filter(
                Q(user__username__icontains=search) |  # 搜学号/工号
                Q(user__first_name__icontains=search) |  # 搜真实姓名
                Q(department__icontains=search)  # 搜部门
            )

        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)


class UserDetailView(generics.RetrieveDestroyAPIView):
    """
    用户详情与删除（仅管理员）
    使用 generics 可以大幅精简代码
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_url_kwarg = 'user_id'

    def get_object(self):
        # 覆写 get_object 以便通过 profile 返回数据
        user = super().get_object()
        return user.profile
