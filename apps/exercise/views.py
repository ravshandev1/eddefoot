from rest_framework import generics
from . import serializers
from .models import Rate, Modul, Theme, Exercise
from .paginations import CustomPagination
from user.permissions import IsStudentUser


class RateAPI(generics.ListAPIView):
    queryset = Rate.objects.all()
    serializer_class = serializers.RateSerializer
    pagination_class = CustomPagination


class ModulAPI(generics.ListAPIView):
    permission_classes = [IsStudentUser]
    pagination_class = CustomPagination
    serializer_class = serializers.ModulSerializer

    def get_queryset(self):
        return Modul.objects.filter(rate__price__lte=self.request.user.rate.price).order_by('ordinal_number')


class ThemeAPI(generics.ListAPIView):
    serializer_class = serializers.ThemeSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Theme.objects.filter(modul_id=self.kwargs.get('pk')).order_by('ordinal_number')


class ExerciseAPI(generics.ListAPIView):
    permission_classes = [IsStudentUser]
    serializer_class = serializers.ExerciseSerializer
    pagination_class = CustomPagination

    @staticmethod
    def return_ordinal_number(obj):
        return obj.ordinal_number

    def get_queryset(self):
        theme_id = self.request.query_params.get('theme_id')
        my_plan_exercises = [i.exercise.id for i in self.request.user.my_plan.all()]
        done_exercises = [i.exercise.id for i in self.request.user.done_exercises.all()]
        rates = [i.id for i in Rate.objects.filter(price__lte=self.request.user.rate.price)]
        lst = list()
        if theme_id:
            qs = Exercise.objects.filter(theme_id=theme_id).order_by('ordinal_number')
        else:
            qs = list()
            for i in rates:
                for j in Exercise.objects.filter(theme__modul__rate_id=i):
                    qs.append(j)
            qs.sort(key=self.return_ordinal_number)
        for i in qs:
            if (i.id not in my_plan_exercises) or (i.id not in done_exercises):
                lst.append(i)
        return lst
