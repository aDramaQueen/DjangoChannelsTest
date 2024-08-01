__author__ = 'Richard Saeuberlich'

from django.urls import path

from messenger.views import NotificationView, MessageOverview, UserMessageView, GroupMessageView

urlpatterns = [
    path('', NotificationView.as_view(), name='notifications'),
    path('overview', MessageOverview.as_view(), name='message-overview'),
    path('user/<int:identifier>', UserMessageView.as_view(), name='user-message'),
    path('group/<int:identifier>', GroupMessageView.as_view(), name='group-message'),
]
