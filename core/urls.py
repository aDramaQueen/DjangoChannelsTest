from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('messenger.urls')),
    path('admin/', admin.site.urls),
    # @see https://docs.djangoproject.com/en/5.0/topics/i18n/translation/#the-set-language-redirect-view
    path('i18n/', include('django.conf.urls.i18n')),
]

# Serve static files in development
# @see https://docs.djangoproject.com/en/5.0/howto/static-files/#serving-static-files-during-development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
