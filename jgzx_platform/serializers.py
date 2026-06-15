from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import UserProfile, Project
from .moderation import raise_if_sensitive


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


# ==========================================
# 项目发布模块 — 序列化器
# ==========================================

def _validate_skill_requirements(value, recruit_count):
    """技能要求：支持 [{"desc":"...", "count": n}] 或 ["str", ...]"""
    if not value:
        return
    if not isinstance(value, list):
        raise serializers.ValidationError('技能要求必须是数组')
    if len(value) > 10:
        raise serializers.ValidationError('技能要求最多 10 条')
    total = 0
    for i, item in enumerate(value):
        if isinstance(item, dict):
            desc = item.get('desc') or item.get('text') or ''
            cnt = item.get('count', 1)
            if not isinstance(desc, str) or len(desc.strip()) == 0:
                raise serializers.ValidationError(f'第 {i+1} 条描述不能为空')
            if len(desc) > 100:
                raise serializers.ValidationError(f'第 {i+1} 条描述不超过 100 字')
            if not isinstance(cnt, int) or cnt < 1 or cnt > 10:
                raise serializers.ValidationError(f'第 {i+1} 条人数须为 1–10')
            total += cnt
        elif isinstance(item, str):
            s = (item or '').strip()
            if len(s) == 0:
                raise serializers.ValidationError(f'第 {i+1} 条不能为空')
            if len(s) > 50:
                raise serializers.ValidationError(f'第 {i+1} 条不超过 50 字')
            total += 1
        else:
            raise serializers.ValidationError(f'第 {i+1} 条格式不正确')
    if total > recruit_count:
        raise serializers.ValidationError(
            f'技能需求总人数({total})不能超过招募人数({recruit_count})'
        )


def _validate_tags(value):
    """自定义标签：字符串数组，最多 5 个，每个 1–20 字"""
    if not value:
        return []
    if not isinstance(value, list):
        raise serializers.ValidationError('标签必须是数组')
    if len(value) > 5:
        raise serializers.ValidationError('标签最多 5 个')
    normalized = []
    seen = set()
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise serializers.ValidationError(f'第 {i+1} 个标签格式不正确')
        s = item.strip()
        if not s:
            continue
        if len(s) > 20:
            raise serializers.ValidationError(f'第 {i+1} 个标签不超过 20 字')
        if s in seen:
            continue
        seen.add(s)
        normalized.append(s)
    if len(normalized) > 5:
        raise serializers.ValidationError('标签最多 5 个')
    return normalized


class ProjectListSerializer(serializers.ModelSerializer):
    """项目列表（公开/我的）"""
    publisher_name = serializers.CharField(source='publisher.first_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    publisher_role_display = serializers.CharField(source='get_publisher_role_display', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'title', 'category', 'category_display', 'status', 'status_display',
            'publisher_role', 'publisher_role_display', 'publisher_name',
            'recruit_count', 'tags', 'deadline', 'created_at', 'published_at',
            'is_visible_when_ended', 'version'
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    """项目详情"""
    publisher_id = serializers.IntegerField(source='publisher.id', read_only=True)
    publisher_name = serializers.CharField(source='publisher.first_name', read_only=True)
    publisher_username = serializers.CharField(source='publisher.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    publisher_role_display = serializers.CharField(source='get_publisher_role_display', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id', 'publisher_id', 'publisher_name', 'publisher_username', 'publisher_role',
            'publisher_role_display', 'title', 'description', 'category', 'category_display',
            'status', 'status_display', 'recruit_count', 'contact_info', 'tags', 'skill_requirements', 'deadline',
            'is_visible_when_ended', 'offline_reason', 'offline_at', 'reject_reason',
            'submitted_at', 'published_at', 'created_at', 'updated_at', 'version'
        )


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """创建/更新项目（标题、描述、类别、招募人数、技能要求、截止时间、是否结束可见）"""
    skill_requirements = serializers.JSONField(required=False, default=list)
    tags = serializers.JSONField(required=False, default=list)

    class Meta:
        model = Project
        fields = (
            'title', 'description', 'category', 'recruit_count', 'contact_info', 'tags',
            'skill_requirements', 'deadline', 'is_visible_when_ended'
        )

    def validate_title(self, value):
        s = (value or '').strip()
        if len(s) == 0:
            raise serializers.ValidationError('标题不能为空')
        if len(s) > 100:
            raise serializers.ValidationError('标题不超过 100 字')
        raise_if_sensitive(s, '标题')
        return s

    def validate_description(self, value):
        s = (value or '').strip()
        if len(s) < 100:
            raise serializers.ValidationError('项目描述至少 100 字')
        if len(s) > 5000:
            raise serializers.ValidationError('项目描述不超过 5000 字')
        raise_if_sensitive(s, '项目描述')
        return s

    def validate_recruit_count(self, value):
        if value is None:
            raise serializers.ValidationError('招募人数必填')
        if not isinstance(value, int) or value < 1 or value > 20:
            raise serializers.ValidationError('招募人数须为 1–20')
        return value

    def validate_contact_info(self, value):
        s = (value or '').strip()
        if len(s) > 200:
            raise serializers.ValidationError('联系方式不超过 200 字')
        return s

    def validate_tags(self, value):
        tags = _validate_tags(value)
        for tag in tags:
            raise_if_sensitive(tag, '自定义标签')
        return tags

    def validate_deadline(self, value):
        if not value:
            raise serializers.ValidationError('截止时间必填')
        now = timezone.now()
        if timezone.is_aware(value):
            value = timezone.make_naive(value, timezone.get_current_timezone())
        if timezone.is_aware(now):
            now = timezone.make_naive(now, timezone.get_current_timezone())
        if value <= now:
            raise serializers.ValidationError('截止时间须大于当前时间')
        return value

    def validate(self, attrs):
        recruit_count = attrs.get('recruit_count')
        if recruit_count is None and self.instance:
            recruit_count = self.instance.recruit_count
        skill = attrs.get('skill_requirements')
        if skill is not None:
            _validate_skill_requirements(skill, recruit_count or 1)
            for item in skill:
                if isinstance(item, dict):
                    desc = (item.get('desc') or item.get('text') or '').strip()
                    if desc:
                        raise_if_sensitive(desc, '技能要求')
                elif isinstance(item, str) and item.strip():
                    raise_if_sensitive(item.strip(), '技能要求')
        return attrs


class RejectBodySerializer(serializers.Serializer):
    reject_reason = serializers.CharField(max_length=500, allow_blank=False)


class OfflineBodySerializer(serializers.Serializer):
    offline_reason = serializers.CharField(max_length=500, allow_blank=False)


class CloseRecruitBodySerializer(serializers.Serializer):
    target = serializers.ChoiceField(choices=['recruit_full', 'ended'])
