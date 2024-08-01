"""
Collection of DTOs that are meant to be sent via "Django Channels - (synchronous/asynchronous) JSON Consumers".

NOTE: If you want to set attributes in frozen dataclasses, you have to use special ``__setattr__`` functions (@see `Python DOCs - Data Classes <https://docs.python.org/3/library/dataclasses.html#frozen-instances>`__)

@see `Django Channels DOCs - Generic Consumers <https://channels.readthedocs.io/en/latest/topics/consumers.html#jsonwebsocketconsumer>`__
"""
__all__ = ('UnknownDTO', 'ErrorDTO', 'NotificationDTO', 'UserTextMessageDTO', 'GroupTextMessageDTO', 'AlertDTO')

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Any, Self

from messenger.constants import MESSAGE_TYPE_KEYWORD, MessageType


@dataclass(slots=True, frozen=True, init=False)
class AbstractMessageDTO(ABC):
    MESSAGE_TYPE: ClassVar[MessageType]

    @classmethod
    @abstractmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        """
        Deserialize JSON data into this DTO

        :param data: JSON data
        :return: This DTO that holds the given data
        """
        ...

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        """
        Serialize this DTO into JSON data

        :return: JSON data
        """
        ...


@dataclass(slots=True, frozen=True, init=False)
class UnknownDTO(AbstractMessageDTO):
    MESSAGE_TYPE = MessageType.UNKNOWN

    def __init__(self) -> None:
        """
        If an unknown message type is sent via Django Channels,
        this DTO should be sent back to make clear something went wrong.

        @see :class:`messenger.constants.MessageType`
        """
        pass

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        return cls()

    def serialize(self) -> dict[str, Any]:
        return {
            MESSAGE_TYPE_KEYWORD: int(self.MESSAGE_TYPE)
        }


@dataclass(slots=True, frozen=True, init=False)
class ErrorDTO(AbstractMessageDTO):
    MESSAGE_TYPE = MessageType.ERROR
    error_code: int
    error_message: str

    def __init__(self, error_code: int, error_message: str) -> None:
        """
        If an error occurred triggered via Django Channels request/response,
        this DTO should be sent back to make clear something went wrong.

        :param error_code: Error code
        :param error_message: More specific error message
        """
        object.__setattr__(self, 'error_code', error_code)
        object.__setattr__(self, 'error_message', error_message)

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        return cls(data['errorCode'], data['errorMessage'])

    def serialize(self) -> dict[str, Any]:
        return {
            MESSAGE_TYPE_KEYWORD: int(self.MESSAGE_TYPE),
            'errorCode': self.error_code,
            'errorMessage': self.error_message,
        }


@dataclass(slots=True, frozen=True, init=False)
class NotificationDTO(AbstractMessageDTO):
    MESSAGE_TYPE = MessageType.NOTIFICATION
    unread_messages: int

    def __init__(self, unread_messages: int) -> None:
        object.__setattr__(self, 'unread_messages', unread_messages)

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        return cls(data['unreadMessages'])

    def serialize(self) -> dict[str, Any]:
        return {
            MESSAGE_TYPE_KEYWORD: int(self.MESSAGE_TYPE),
            'unreadMessages': self.unread_messages
        }


@dataclass(slots=True, frozen=True, init=False)
class UserTextMessageDTO(AbstractMessageDTO):
    MESSAGE_TYPE = MessageType.USER_TEXT_MESSAGE

    def __init__(self) -> None:
        # Do your thing...
        pass

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        # Do your thing...
        pass

    def serialize(self) -> dict[str, Any]:
        return {
            MESSAGE_TYPE_KEYWORD: int(self.MESSAGE_TYPE),
            # Do your thing...
        }


@dataclass(slots=True, frozen=True, init=False)
class GroupTextMessageDTO(AbstractMessageDTO):
    MESSAGE_TYPE = MessageType.GROUP_TEXT_MESSAGE

    def __init__(self) -> None:
        # Do your thing...
        pass

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        # Do your thing...
        pass

    def serialize(self) -> dict[str, Any]:
        return {
            MESSAGE_TYPE_KEYWORD: int(self.MESSAGE_TYPE),
            # Do your thing...
        }


@dataclass(slots=True, frozen=True, init=False)
class AlertDTO(AbstractMessageDTO):
    MESSAGE_TYPE = MessageType.ALERT

    def __init__(self) -> None:
        # Do your thing...
        pass

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        # Do your thing...
        pass

    def serialize(self) -> dict[str, Any]:
        return {
            MESSAGE_TYPE_KEYWORD: int(self.MESSAGE_TYPE),
            # Do your thing...
        }
