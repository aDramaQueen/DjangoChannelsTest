from typing import Optional

from django.contrib.admin import ModelAdmin, register, display
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from messenger.models import Notification, UserTextMessage, GroupTextMessage, ChannelUser


@register(ChannelUser)
class ChannelUserAdmin(ModelAdmin):
    filter_horizontal = ('groups', 'user_permissions')


@register(Notification)
class NotificationAdmin(ModelAdmin):
    readonly_fields = ('user', )

    # Deactivate adding new notifications, it's a one-to-one relationship, and it is created automatically!
    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    # Deactivate deleting notifications, since this is done automatically!
    def has_delete_permission(self, request: HttpRequest, obj: Optional[Notification] = None) -> bool:
        return False


@register(UserTextMessage)
class UserTextMessageAdmin(ModelAdmin):
    readonly_fields = ('created', )
    list_display = ('title', 'created', 'user', 'received')


@register(GroupTextMessage)
class GroupTextMessageAdmin(ModelAdmin):
    filter_horizontal = ('target_group', 'received_group')
    readonly_fields = ('created', )
    list_display = ('title', 'users_received')

    @display(description=_('Users received'))
    def users_received(self, instance: GroupTextMessage) -> int:
        return instance.received_group.count()
