from rest_framework import serializers
from .models import ProjectThreadComment
from .moderation import raise_if_sensitive


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=2000)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_content(self, value):
        text = (value or '').strip()
        if len(text) < 2:
            raise serializers.ValidationError('评论内容至少 2 个字符')
        raise_if_sensitive(text, '评论内容')
        return text


class CommentTreeItemSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.first_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    can_delete = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ProjectThreadComment
        fields = (
            'id',
            'project_id',
            'parent_id',
            'content',
            'is_deleted',
            'author_name',
            'author_username',
            'created_at',
            'updated_at',
            'can_delete',
            'replies',
        )

    def get_can_delete(self, obj):
        user = self.context.get('request').user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or user.id == obj.author_id

    def get_replies(self, obj):
        children = getattr(obj, 'prefetched_replies', None)
        if children is None:
            children = obj.replies.filter(is_deleted=False).select_related('author')
        return CommentTreeReplySerializer(
            children, many=True, context=self.context
        ).data


class CommentTreeReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.first_name', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = ProjectThreadComment
        fields = (
            'id',
            'project_id',
            'parent_id',
            'content',
            'is_deleted',
            'author_name',
            'author_username',
            'created_at',
            'updated_at',
            'can_delete',
        )

    def get_can_delete(self, obj):
        user = self.context.get('request').user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or user.id == obj.author_id
