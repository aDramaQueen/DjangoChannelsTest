import datetime
from abc import abstractmethod, ABC
from logging import getLogger
from typing import Any, Optional

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from messenger.constants import MessageType, MESSAGE_TYPE_KEYWORD
from messenger.dto import UnknownDTO, NotificationDTO, ErrorDTO
from messenger.models import Notification, ChannelUser

LOGGER = getLogger(__name__)


class MessengerConsumer(AsyncJsonWebsocketConsumer, ABC):

    @abstractmethod
    async def remember_group(self, channel_name: str) -> None:
        ...

    @abstractmethod
    async def forget_group(self, channel_name: str) -> None:
        ...

    @abstractmethod
    async def group_exists(self, channel_name: str) -> bool:
        ...

    async def connect(self) -> None:
        current_user: ChannelUser = self.scope['user']
        if current_user.is_anonymous:
            raise DenyConnection('Unauthorized user')
        else:
            now = datetime.datetime.now()
            await self.channel_layer.group_add(
                current_user.get_channel_name(),
                self.channel_name
            )
            exec_time = (datetime.datetime.now() - now)
            print(f'CONNECT: {exec_time.total_seconds()}s')
            await self.accept()
            await self.remember_group(self.channel_name)

    async def disconnect(self, close_code: int):
        current_user: ChannelUser = self.scope['user']
        if not current_user.is_anonymous:
            await self.forget_group(self.channel_name)
            await self.channel_layer.group_discard(
                current_user.get_channel_name(),
                self.channel_name
            )

    async def receive_json(self, content: dict[str, Any], **kwargs):
        try:
            message_type: Optional[MessageType] = MessageType.get_message_type(content[MESSAGE_TYPE_KEYWORD])
        except ValueError:
            message_type: Optional[MessageType] = None
        match message_type:
            case MessageType.UNKNOWN:
                # User didn't understand last sent message type
                LOGGER.error(f'Last message sent to user "{self.scope['user']}" could NOT be processed, since he did not know the used message type!')
            case MessageType.ERROR:
                # User threw error
                error_dto = ErrorDTO.deserialize(content)
                LOGGER.error(f'User threw error.\n\tERROR CODE: {error_dto.error_code}\n\tERROR MESSAGE: {error_dto.error_message}')
            case MessageType.NOTIFICATION:
                # User wants a notification update
                current_user: ChannelUser = self.scope['user']
                notifications: Notification = await Notification.objects.aget(user=current_user)
                await self.send_json(NotificationDTO(notifications.unread_messages).serialize())
            case MessageType.USER_TEXT_MESSAGE:
                # User wants to send a text message to other user
                raise NotImplementedError('User text message type currently not supported')
            case MessageType.GROUP_TEXT_MESSAGE:
                # User wants to send a text message to multiple other users
                raise NotImplementedError('Group text message type currently not supported')
            case MessageType.ALERT:
                # User wants..., ?!?
                raise NotImplementedError('Alert message type currently not supported')
            case _:
                LOGGER.error(f'Unknown message type "{message_type}" from user "{self.scope['user']}"')
                await self.send_json(UnknownDTO().serialize())

    # NOTE: Function name must be same as the "type" in "message.signals.notification" function
    async def send_notification(self, data: dict[str, Any]) -> None:
        if await self.group_exists(self.channel_name):
            await self.send_json(data['dto'].serialize())


class MessengerConsumerDevelopment(MessengerConsumer):
    """
    @see https://channels.readthedocs.io/en/latest/topics/channel_layers.html#single-channels
    """

    _GROUPS: dict[str, int] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

    async def remember_group(self, channel_name: str) -> None:
        number_of_users = self._GROUPS.get(channel_name, 0)
        self._GROUPS[channel_name] = number_of_users + 1

    async def forget_group(self, channel_name: str) -> None:
        number_of_users = self._GROUPS.get(channel_name, 0)
        if number_of_users > 1:
            self._GROUPS[channel_name] = number_of_users - 1
        else:
            self._GROUPS.pop(channel_name, None)

    @classmethod
    async def group_exists(cls, channel_name: str) -> bool:
        return channel_name in cls._GROUPS.keys()


class MessengerConsumerProduction(MessengerConsumer):
    """
    @see https://channels.readthedocs.io/en/latest/topics/channel_layers.html#single-channels
    """

    async def remember_group(self, channel_name: str) -> None:
        # In memory DB
        # TODO...
        redis = await aioredis.create_redis_pool('redis://localhost')
        await redis.sadd(f"group_{channel_name}_members", self.channel_name)
        redis.close()
        await redis.wait_closed()

    async def forget_group(self, channel_name: str) -> None:
        assert False, 'INSTALL REDDIS TO USE THIS'
        # In memory DB
        # TODO...
        redis = await aioredis.create_redis_pool('redis://localhost')
        await redis.srem(f"group_{channel_name}_members", self.channel_name)
        redis.close()
        await redis.wait_closed()

    async def group_exists(self, channel_name: str) -> bool:
        assert False, 'INSTALL REDDIS TO USE THIS'
        # In memory DB
        # TODO...
        redis = await aioredis.create_redis_pool('redis://localhost')
        group_members = await redis.smembers(f"group_{group_name}_members")
        redis.close()
        await redis.wait_closed()
        return len(group_members) > 0
