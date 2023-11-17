from rest_framework import serializers
from .models import Rate, Modul, Theme, Exercise


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id', 'price', 'description']


class ModulSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modul
        fields = ['id', 'ordinal_number', 'image_path', 'name', 'themes_count']

    themes_count = serializers.IntegerField(source='themes.count')


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'ordinal_number', 'name', 'image', 'exercises_count']

    exercises_count = serializers.IntegerField(source='exercises.count')


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'ordinal_number', 'do_day', 'image', 'video', 'description']
