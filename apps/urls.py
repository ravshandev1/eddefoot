from django.urls import include, path

urlpatterns = [
    path('', include('exercise.urls')),
    path('user/', include('user.urls')),
]
