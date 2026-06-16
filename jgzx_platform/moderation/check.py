"""内容审核入口：供序列化器调用。"""
from django.conf import settings
from rest_framework import serializers

from .dfa_filter import get_dfa_filter

DEFAULT_MESSAGE = '包含违规信息，请修改后再发布'


def is_moderation_enabled() -> bool:
    return getattr(settings, 'CONTENT_MODERATION_ENABLED', True)


def contains_sensitive(text: str) -> bool:
    if not is_moderation_enabled():
        return False
    return get_dfa_filter().contains(text or '')


def raise_if_sensitive(text: str, field_label: str = '内容') -> None:
    """命中敏感词时抛出 DRF 校验错误（不暴露具体敏感词）。"""
    if not text or not str(text).strip():
        return
    if contains_sensitive(str(text)):
        raise serializers.ValidationError(f'{field_label}{DEFAULT_MESSAGE}')
