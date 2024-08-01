from typing import TypeVar

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete, m2m_changed, pre_delete
from django.dispatch import receiver

from messenger.dto import NotificationDTO
from messenger.models import (
    Notification, ChannelUser, UserTextMessage, GroupTextMessage, AbstractGroupMessage, AbstractUserMessage
)

UserMessage = TypeVar('UserMessage', bound=AbstractUserMessage)
GroupMessage = TypeVar('GroupMessage', bound=AbstractGroupMessage)


def _notify_user(note: Notification) -> None:
    """
    Sends notification update to user that ows this notification.

    :param note: Notification
    """
    channel_layer = get_channel_layer()
    # NOTE: You must create a function in the "message.consumers.NotificationConsumer"
    #       class that has the same name as the "type" element from below.
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            note.user.get_channel_name(), {
                'type': 'send_notification',  # same name as function in "message.consumers.MessageConsumer"
                'dto': NotificationDTO(note.unread_messages)
            }
        )


async def _notify_user_async(note: Notification) -> None:
    """
    Asynchronous variant of ``_notify_user(note: Notification)``

    :param note: Notification
    """
    channel_layer = get_channel_layer()
    # NOTE: You must create a function in the "message.consumers.NotificationConsumer"
    #       class that has the same name as the "type" element from below.
    if channel_layer is not None:
        await channel_layer.group_send(
            note.user.get_channel_name(), {
                'type': 'send_notification',  # same name as function in "message.consumers.MessageConsumer"
                'dto': NotificationDTO(note.unread_messages)
            }
        )


@receiver(post_save, sender=ChannelUser)
def create_user_notification(sender: type[ChannelUser], instance: ChannelUser, created, **kwargs) -> None:
    """
    If a user is created, automatically create the notification model with a one-to-one relationship!

    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    """
    if created:
        Notification.objects.create(user=instance)


@receiver(post_save, sender=UserTextMessage)
def trigger_user_message_notification(sender: type[UserMessage], instance: UserMessage, created, **kwargs) -> None:
    """
    If a new user message is created, automatically increment user notification by 1.

    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        instance.trigger_notification()


@receiver(post_delete, sender=UserTextMessage)
def never_received_user_message(sender: type[UserMessage], instance: UserMessage, using, origin, **kwargs) -> None:
    """
    If a user message is deleted, that never was read by the user, reduce his notification counter,
    because he no longer can read this message!

    :param sender:
    :param instance:
    :param using:
    :param origin:
    :param kwargs:
    """
    if not instance.received:
        instance.user.notification.read_one_message()


@receiver(m2m_changed, sender=GroupTextMessage.target_group.through)
def trigger_group_message_notification(sender: type[GroupMessage], instance: GroupMessage, action: str, reverse: bool, model: type[GroupMessage], pk_set: set[int], using: str, **kwargs) -> None:
    """
    If a new group message is created, automatically increment user notification by 1.

    :param sender: Child model of `AbstractGroupMessage`
    :param instance: Instance of model
    :param action:
    :param reverse:
    :param model: Child model of `AbstractGroupMessage`
    :param pk_set: Set of primary keys of target users
    :param using:
    :param kwargs: Additional keyword arguments
    """
    if action == 'post_add':
        # Only trigger mechanism if save was successfully!
        notifications = [user.notification for user in ChannelUser.objects.filter(pk__in=pk_set)]
        for note in notifications:
            note.unread_messages += 1
        Notification.objects.bulk_update(notifications, ('unread_messages', ))
        for note in notifications:
            _notify_user(note)


@receiver(pre_delete, sender=GroupTextMessage)
def never_received_group_message(sender: type[GroupMessage], instance: GroupMessage, using: str, origin, **kwargs) -> None:
    """
    If a group message is deleted, that never was read by a user, reduce his notification counter,
    because he no longer can read this message!

    :param sender:
    :param instance:
    :param using:
    :param origin:
    :param kwargs:
    """
    # @see https://docs.djangoproject.com/en/5.0/ref/models/querysets/#exclude
    notifications = [user.notification for user in instance.target_group.all().exclude(pk__in=instance.received_group.all())]
    for note in notifications:
        if note.unread_messages > 0:
            note.unread_messages -= 1
    Notification.objects.bulk_update(notifications, ('unread_messages', ))
    for note in notifications:
        _notify_user(note)


@receiver(post_save, sender=Notification)
def notification(sender: type[Notification], instance: Notification, created, **kwargs) -> None:
    """
    If the notification model for a user changes, notify this user via websocket call

    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    """
    if not created:
        _notify_user(instance)
