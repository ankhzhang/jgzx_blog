from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import userviews  # 指向更名后的 userview.py

# 使用 DefaultRouter 处理那些基于标准动作（如 List, Retrieve）的接口
# 虽然你目前大多使用 APIView，但为了以后扩展方便，保留 Router 结构是好习惯
router = DefaultRouter()

urlpatterns = [
    # ==========================================
    # 1. 认证相关接口 (无需登录)
    # ==========================================
    path('register/', userviews.RegisterView.as_view(), name='user-register'),
    path('login/', userviews.LoginView.as_view(), name='user-login'),

    # ==========================================
    # 2. 个人中心接口 (必须登录)
    # ==========================================
    path('logout/', userviews.LogoutView.as_view(), name='user-logout'),
    path('profile/', userviews.UserProfileView.as_view(), name='user-profile'),  # 获取/更新个人资料
    path('change-password/', userviews.ChangePasswordView.as_view(), name='change-password'),

    # ==========================================
    # 3. 管理员接口 (仅限 IsAdminUser)
    # ==========================================
    path('bulk-register/', userviews.BulkRegisterView.as_view(), name='bulk-register'),
    path('users/', userviews.UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', userviews.UserDetailView.as_view(), name='user-detail'),

    # 包含 Router 生成的路由（如果未来增加了 ViewSet）
    path('', include(router.urls)),
]