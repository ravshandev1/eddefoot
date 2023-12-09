from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import render


def home(req):
    return render(req, 'chat.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('api/v1/', include('apps.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    *i18n_patterns(*urlpatterns, prefix_default_language=True),
]
