from django.conf import settings
from django.urls import re_path

from messenger.consumers import MessengerConsumerDevelopment, MessengerConsumerProduction, MessengerConsumer

__consumer = MessengerConsumerDevelopment if settings.DEBUG else MessengerConsumerProduction

if settings.DEBUG:
    # Regex Path
    # @see https://docs.djangoproject.com/en/5.0/ref/urls/#re-path
    websocket_notification_urlpatterns = [
        re_path(r'ws/notify/', __consumer.as_asgi()),
    ]
else:
    # Regex Path
    # @see https://docs.djangoproject.com/en/5.0/ref/urls/#re-path
    websocket_notification_urlpatterns = [
        re_path(r'ws/notify/', __consumer.as_asgi()),
    ]


async def does_group_exist(group_name: str) -> bool:
    return await __consumer.group_exists(group_name)
