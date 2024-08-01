from enum import IntEnum, unique
from typing import Self

MESSAGE_TYPE_KEYWORD: str = 'messageType'


@unique
class MessageType(IntEnum):
    """ Enumeration of all known message types within this application """
    UNKNOWN = 0
    ERROR = 1
    NOTIFICATION = 2
    USER_TEXT_MESSAGE = 3
    GROUP_TEXT_MESSAGE = 4
    ALERT = 5

    @classmethod
    def get_django_choices(cls) -> list[tuple[int, str]]:
        """
        Returns a Django choice list of message types

        Example::

            result = [
                (0, 'UNKNOWN'),
                (1, 'ERROR'),
                ...
            ]

        @see `Django DOCs - Model field reference <https://docs.djangoproject.com/en/5.0/ref/models/fields/#choices>`__
        :return: Django choice list
        """
        return [(m_type.value, m_type.name) for m_type in cls]

    @classmethod
    def get_dictionary(cls) -> dict[str, int]:
        """
        Returns a dictionary of message type names mapping to their integer identifier.

        Example::

            result = {
                'UNKNOWN': 0,
                'ERROR': 1,
                ...
            }

        :return: Message type name mapper
        """
        return {m_type.name: m_type.value for m_type in cls}

    @classmethod
    def get_message_type(cls, identifier: int) -> Self:
        """
        Returns the message type associated with the given (integer) identifier

        :param identifier: Message type identifier
        :return: Message type enumeration
        :raise ValueError If given identifier does not fit with any known message type identifier
        """
        for m_type in cls:
            if m_type.value == identifier:
                return m_type
        raise ValueError(f'Unknown message type: {identifier}')
