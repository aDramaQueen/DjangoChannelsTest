from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messenger'

    def ready(self):
        # ATTENTION: Leave the imports here!!!
        # @see https://docs.djangoproject.com/en/5.0/topics/signals/#connecting-receiver-functions
        import messenger.signals
