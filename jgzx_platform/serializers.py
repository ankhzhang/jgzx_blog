from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import UserProfile


# ==========================================
# 1. 用户注册序列化器
# ==========================================
class UserRegisterSerializer(serializers.ModelSerializer):
    """
    负责 User 和 UserProfile 的同步创建。
    - username: 学号/工号
    - first_name: 真实姓名
    - email: 设为非必填 (required=False)
    - password: 自动哈希加密存储 (set_password)
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    real_name = serializers.CharField(source='first_name', required=True, allow_blank=False)

    # 业务身份与扩展字段
    identity = serializers.ChoiceField(choices=UserProfile.IDENTITY_CHOICES, required=True)
    phone = serializers.CharField(required=True, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'real_name',
                  'identity', 'phone', 'department')
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False,
                         'help_text': '请输入学号', 'error_messages': {'unique': '该学号已被注册'}},
        }

    def validate(self, attrs):
        # 两次密码校验
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs

    def create(self, validated_data):
        # 使用事务保证原子性：User和Profile要么全成功，要么全失败
        with transaction.atomic():
            # 提取Profile数据
            profile_fields = ['identity', 'phone', 'department']
            profile_data = {f: validated_data.pop(f, '') for f in profile_fields}

            validated_data.pop('password2')
            password = validated_data.pop('password')

            # 1. 创建 User
            user = User.objects.create(**validated_data)
            user.set_password(password)  # 加密
            user.save()

            # 2. 更新自动生成的 Profile (Signals 机制)
            profile = user.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

            return user


# ==========================================
# 2. 批量注册序列化器
# ==========================================
class BulkUserRegisterSerializer(serializers.Serializer):
    """
    接收用户数组进行批量注册，支持部分成功并返回错误清单
    """
    users = UserRegisterSerializer(many=True)

    def create(self, validated_data):
        user_list = validated_data.get('users')
        success_list = []
        errors_list = []

        for index, user_data in enumerate(user_list):
            # 为每一条数据开启独立的原子事务
            try:
                with transaction.atomic():
                    # 这里的 create 是单条 UserRegisterSerializer 的逻辑
                    serializer = UserRegisterSerializer()
                    user = serializer.create(user_data)
                    success_list.append(user.username)
            except Exception as e:
                # 记录报错的具体行数和错误原因
                errors_list.append({
                    "row_index": index + 1,
                    "username": user_data.get('username', '未知'),
                    "error": str(e)
                })

        return {
            "total": len(user_list),
            "success_count": len(success_list),
            "error_count": len(errors_list),
            "errors": errors_list,  # 返回给前端，方便管理员查看哪几个没录入成功
            "success_usernames": success_list
        }


# ==========================================
# 3. 用户资料展示序列化器 (包含所有扩展字段)
# ==========================================
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    real_name = serializers.CharField(source='user.first_name', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    # ✅ 暴露 is_staff 字段
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'real_name', 'identity', 'phone', 'department',
                  'avatar', 'bio', 'project_count', 'comment_count',
                  'is_banned', 'date_joined', 'created_at', 'updated_at', 'is_staff')
        # 核心业务字段只读，防止通过该接口被篡改
        read_only_fields = ('identity', 'project_count', 'comment_count', 'is_banned', 'is_staff')


# ==========================================
# 4. 用户资料更新序列化器 (展平化设计)
# ==========================================
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    展平化设计：前端直接发送 phone, department, bio 等字段
    仅允许用户更新：联系电话、部门、个人简介、头像。
    禁止更新：真实姓名、学号、身份。
    """
    phone = serializers.CharField(source='profile.phone', required=False, allow_blank=True)
    department = serializers.CharField(source='profile.department', required=False, allow_blank=True)
    bio = serializers.CharField(source='profile.bio', required=False, allow_blank=True)
    avatar = serializers.ImageField(source='profile.avatar', required=False)

    # 身份和学号注册后不可自改
    identity = serializers.CharField(source='profile.identity', read_only=True)
    username = serializers.CharField(read_only=True)
    real_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = User
        fields = ('real_name', 'username', 'identity', 'phone', 'department', 'bio', 'avatar')
        read_only_fields = ('real_name', 'account', 'identity')

    def update(self, instance, validated_data):
        # 1. 处理展平的 Profile 数据 (DRF source 机制会将其放入 'profile' key 中)
        profile_data = validated_data.pop('profile', {})

        # 2. 更新 User 表
        # 如果未来有 User 表的其他非核心字段修改，可在此扩展

        # 3. 更新 UserProfile 表
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


# ==========================================
# 5. 修改密码序列化器(仅用于用户个人中心)
# ==========================================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "两次新密码不一致"})
        return attrs
