from abc import abstractmethod

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    Model, CharField, ForeignKey, CASCADE, ManyToManyField, BooleanField, Q, DateTimeField, OneToOneField,
    PositiveIntegerField, TextField
)
from django.utils.translation import gettext_lazy as _

from messenger.constants import MessageType


class ChannelUser(AbstractUser):

    def get_channel_name(self) -> str:
        """
        "Django Channels" group names are restricted to ASCII alphanumerics, hyphens, and periods only and are limited
        to a maximum length of 100 in the default backend.

        :return: Channel name
        """
        return f'message_{self.pk}'


class AbstractMessageType(Model):
    # NOTE: This field will always use the servers default timezone
    # @see https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/#default-current-time-zone
    created = DateTimeField(
        auto_now_add=True, editable=False,
        help_text=_('Date & time this message was created.')
    )

    @staticmethod
    @abstractmethod
    def get_number_of_unread_messages(user: ChannelUser) -> int:
        raise NotImplementedError('This abstract message has no number of unread messages')

    @staticmethod
    @abstractmethod
    def message_type() -> MessageType:
        # NOTE: Overwrite this in none-abstract models that are actually saved to the DB
        raise NotImplementedError('This abstract message has no message type')

    class Meta:
        abstract = True


class AbstractUserMessage(AbstractMessageType):

    received = BooleanField(
        default=False,
        help_text=''
    )
    # Many-to-one
    user = ForeignKey(
        ChannelUser,
        on_delete=CASCADE,  # If you delete a user, also delete all messages for this user
        limit_choices_to=Q(is_active=True),  # Limit choices to active users
        help_text=''
    )

    class Meta:
        abstract = True

    @classmethod
    def get_number_of_unread_messages(cls, user: ChannelUser) -> int:
        """
        Returns the number of unread user messages for given user

        :param user: User whose unread messages should be counted
        :return: Number of unread user messages
        """
        return cls.objects.filter(user=user, received=False).count()

    def trigger_notification(self) -> None:
        self.user.notification.trigger()


class AbstractGroupMessage(AbstractMessageType):
    """
    ATTENTION: Notification trigger is handled via Signals in ``messenger.signals.trigger_group_message_notification(...)``
    """

    # Many-to-many
    target_group = ManyToManyField(
        ChannelUser,
        limit_choices_to=Q(is_active=True),  # Limit choices to active users
        related_name="%(class)s_target_set",  # @see https://docs.djangoproject.com/en/5.0/topics/db/models/#abstract-related-name
        help_text=''
    )
    # Many-to-many
    received_group = ManyToManyField(
        ChannelUser, blank=True,
        limit_choices_to=Q(is_active=True),  # Limit choices to active users
        related_name="%(class)s_received_set",  # @see https://docs.djangoproject.com/en/5.0/topics/db/models/#abstract-related-name
        help_text='',
    )

    class Meta:
        abstract = True

    @classmethod
    def get_number_of_unread_messages(cls, user: ChannelUser) -> int:
        """
        Returns the number of unread group messages for given user

        :param user: User whose unread messages should be counted
        :return: Number of all unread group messages for given user
        """
        # all_messages = cls.objects.filter(target_group__pk=user.pk)
        # all_received_messages = cls.objects.filter(received_group__pk=user.pk)
        # return all_messages.exclude(received_group__in=all_received_messages).count()
        return cls.objects.filter(target_group__pk=user.pk).exclude(received_group__pk=user.pk).count()

    @classmethod
    def user_received(cls, identifier: int, user: ChannelUser) -> None:
        message: AbstractGroupMessage = cls.objects.get(pk=identifier)
        already_received: set[int] = set(message.received_group.values_list('id', flat=True))
        already_received.add(user.pk)
        # message.received_group = already_received
        message.save(update_fields=('received_group', ))

    def has_read(self, user: ChannelUser) -> bool:
        """
        Determines if given user already has read this message.

        :param user: User to look for
        :return: If user has read this message or not
        """
        return self.received_group.filter(pk=user.pk).exists()


class UserTextMessage(AbstractUserMessage):

    title = CharField(
        max_length=255,
        help_text=_('(max: 255)')
    )
    content = TextField()

    @staticmethod
    def message_type() -> MessageType:
        return MessageType.USER_TEXT_MESSAGE

    def __str__(self) -> str:
        return self.title


class GroupTextMessage(AbstractGroupMessage):
    title = CharField(
        max_length=255,
        help_text=_('(max: 255)')
    )
    content = TextField()

    @staticmethod
    def message_type() -> MessageType:
        return MessageType.GROUP_TEXT_MESSAGE

    def __str__(self) -> str:
        return self.title


class Notification(Model):
    unread_messages = PositiveIntegerField(
        default=0,
        help_text=''
    )
    # One-to-one
    user = OneToOneField(
        ChannelUser, editable=False,
        on_delete=CASCADE,  # If you delete a user, also delete notification for this user
        help_text=''
    )

    @classmethod
    def message_type(cls) -> MessageType:
        return MessageType.NOTIFICATION

    @staticmethod
    def reset_notifications(user: ChannelUser) -> None:
        """
        Searches all `UserTextMessages` & `GroupTextMessages` for given user, that are NOT already marked as received.
        In other words, all messages that are unread. After this search the unread messages counters is reset to the
        overall number of unread messages (`UserTextMessages` & `GroupTextMessages`).

        :param user: User whose notification should be reset
        """
        unread_user_messages = UserTextMessage.objects.filter(user=user, received=False).count()
        unread_group_messages = user.grouptextmessage_target_set.all().exclude(pk__in=(user.pk, )).count()
        note = user.notification
        note.unread_messages = unread_user_messages + unread_group_messages
        note.save()

    def trigger(self) -> None:
        self.unread_messages += 1
        self.save(update_fields=('unread_messages', ))

    def read_one_message(self) -> None:
        if self.unread_messages > 0:
            self.unread_messages -= 1
        self.save(update_fields=('unread_messages', ))

    def clear_notifications(self) -> None:
        self.unread_messages = 0
        self.save(update_fields=('unread_messages', ))

    def __str__(self) -> str:
        return f'Notifications for "{self.user}"'
