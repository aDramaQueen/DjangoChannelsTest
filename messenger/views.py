from dataclasses import dataclass
from datetime import datetime
from operator import attrgetter
from typing import Any, Optional

from django.views.generic import TemplateView

from messenger.constants import MessageType
from messenger.models import UserTextMessage, ChannelUser, GroupTextMessage


class NotificationView(TemplateView):
    template_name = 'messenger/notifications.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Do your thing...
        return context


@dataclass
class MessageMetaData:
    message_type: MessageType
    id: int
    created: datetime
    title: str
    received: bool


class MessageOverview(TemplateView):
    template_name = 'messenger/overview.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user: ChannelUser = self.request.user  # noqa
        # @see messenger.models.AbstractUserMessage.user
        messages: list[MessageMetaData] = [
            MessageMetaData(MessageType.USER_TEXT_MESSAGE, msg.pk, msg.created, msg.title, msg.received) for msg in user.usertextmessage_set.order_by('created').all()
        ]
        # @see messenger.models.AbstractGroupMessage.received_group
        for msg in user.grouptextmessage_target_set.order_by('created').all():
            messages.append(MessageMetaData(MessageType.GROUP_TEXT_MESSAGE, msg.pk, msg.created, msg.title, msg.has_read(user)))
        context['text_messages'] = sorted(messages, key=attrgetter('created'))  # Sort for time of creation
        context['user_message_type'] = MessageType.USER_TEXT_MESSAGE
        context['group_message_type'] = MessageType.GROUP_TEXT_MESSAGE
        return context


class UserMessageView(TemplateView):
    template_name = 'messenger/single-message.html'

    def get_context_data(self, identifier: Optional[int] = None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Mark message as received
        message = UserTextMessage.objects.get(id=identifier)
        message.received = True
        message.save()
        # Trigger notification reduction by 1
        user: ChannelUser = self.request.user  # noqa
        user.notification.read_one_message()
        # Finally present message on view
        context['message'] = message
        return context


class GroupMessageView(TemplateView):
    template_name = 'messenger/single-message.html'

    def get_context_data(self, identifier: Optional[int] = None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user: ChannelUser = self.request.user  # noqa
        # Mark message as received
        message = GroupTextMessage.objects.get(id=identifier)
        if not message.received_group.filter(pk=user.pk).exists():
            message.received_group.add(user)
            message.save()
            # Trigger notification reduction by 1
            user.notification.read_one_message()
        # Finally present message on view
        context['message'] = message
        return context
