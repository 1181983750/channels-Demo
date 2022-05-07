from django.conf.urls.static import static
from django.urls import path, include

from User import urls as user_urls
from Message import urls as message_urls
from django.conf import settings


urlpatterns = [
    path('user/', include(user_urls)),
    path('message/', include(message_urls))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
