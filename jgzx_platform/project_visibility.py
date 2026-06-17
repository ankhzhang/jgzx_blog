"""项目公开可见性（普通用户 B 在公开列表/详情/评论区的可见规则）。

1. 未过截止时间 → B 一定能看见（与「结束后可见」开关无关）
2. 过了截止时间（哪怕还是「已发布」）+ 开关关 → B 看不见
3. 已招满/已结束 + 开关开 → B 能看见
4. 已招满/已结束 + 开关关 → B 看不见

发布者本人、管理员不受此限制。
"""
from django.db.models import Q
from django.utils import timezone


def public_project_visibility_q(*, now=None):
    """普通用户在公开列表中可见项目的 Q 条件。"""
    now = now or timezone.now()
    return (
        # 招募中：已发布且未过截止时间
        Q(status='published', deadline__gt=now)
        | (
            # 已结束（过截止时间或状态为已招满/已结束）且允许对外可见
            Q(status__in=['published', 'recruit_full', 'ended'])
            & (Q(status__in=['recruit_full', 'ended']) | Q(deadline__lte=now))
            & Q(is_visible_when_ended=True)
        )
    )


def is_project_publicly_visible(project, *, now=None) -> bool:
    """普通用户是否可在公开列表/详情查看该项目。"""
    if project.status not in ('published', 'recruit_full', 'ended'):
        return False
    now = now or timezone.now()
    if project.status == 'published' and project.deadline > now:
        return True
    ended = project.status in ('recruit_full', 'ended') or project.deadline <= now
    return ended and project.is_visible_when_ended
