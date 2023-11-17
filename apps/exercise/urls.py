from django.urls import path
from .views import ExerciseAPI, ThemeAPI, ModulAPI, RateAPI

urlpatterns = [
    path('rates/', RateAPI.as_view()),
    path('moduls/', ModulAPI.as_view()),
    path('themes/<int:pk>/', ThemeAPI.as_view()),
    path('exercises/', ExerciseAPI.as_view()),
]
