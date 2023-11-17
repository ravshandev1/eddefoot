from rest_framework import serializers
from .models import User, Level, Age, Feedback, Lesson, DoneExercise, MyPlan, Notification, ExerciseAnswer


class MyPlanModulSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='exercise.theme.modul.id')
    name = serializers.CharField(source='exercise.theme.modul.name')
    image = serializers.CharField(source='exercise.theme.modul.image.url')


class MyPlanThemeSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='exercise.theme.id')
    name = serializers.CharField(source='exercise.theme.name')
    image = serializers.CharField(source='exercise.theme.image.url')


class AnswerExerciseSerializer(serializers.Serializer):
    video = serializers.CharField()
    description = serializers.CharField()
    point = serializers.IntegerField()


class MyPlanExerciseSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='exercise.id')
    percent = serializers.FloatField()
    name = serializers.CharField(source='exercise.name')
    image = serializers.CharField(source='exercise.image.url')
    video = serializers.CharField(source='exercise.video.url')
    description = serializers.CharField(source='exercise.description')
    answers = AnswerExerciseSerializer(many=True, source='exercise.exercise_answers')


class StudentPlanSerializer(serializers.Serializer):
    percent = serializers.FloatField()
    name = serializers.CharField(source='exercise.name')
    description = serializers.CharField(source='exercise.description')
    date = serializers.DateField()
    video = serializers.CharField(source='exercise.video.url')
    answers = AnswerExerciseSerializer(many=True, source='exercise.exercise_answers')


class ExerciseAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseAnswer
        fields = ['user', 'exercise', 'video', 'description']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'text', 'is_read', 'created_at']


class MyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlan
        fields = ['id', 'name', 'video', 'percent', 'description', 'date']

    name = serializers.CharField(source='exercise.name')
    video = serializers.FileField(source='exercise.video.url')
    description = serializers.CharField(source='exercise.description')


class DoneExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoneExercise
        fields = ['name', 'video', 'created_at']

    name = serializers.CharField(source='exercise.name')
    video = serializers.FileField(source='exercise.video.url')


class LessonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'image', 'date']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['sender', 'students', 'name', 'image', 'link', 'password', 'date']


class LessonStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['name', 'image', 'link', 'password', 'date']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['user', 'image', 'video', 'text']


class AgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Age
        fields = ['id', 'name']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'icon', 'subtext']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'role', 'point', 'image']

    role = serializers.CharField(source='get_role_display')


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'image', 'rating']

    rating = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_rating(obj):
        lst = [i.id for i in User.objects.filter(role=0).order_by('-point')]
        return lst.index(obj.id) + 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'image', 'image', 'role_name']

    role_name = serializers.CharField(source='get_role_display', read_only=True)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'image', 'level', 'age', 'gender', 'rating', 'role_name', 'level_name', 'rate',
                  'gender_name', 'rate_name', 'age_name']

    role_name = serializers.CharField(source='get_role_display', read_only=True)
    rate_name = serializers.CharField(source='rate.price', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    age_name = serializers.CharField(source='age.name', read_only=True)
    gender_name = serializers.CharField(source='get_gender_display', read_only=True)
    gender = serializers.IntegerField(write_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_rating(obj):
        lst = [i.id for i in User.objects.filter(role=0).order_by('-point')]
        return lst.index(obj.id) + 1
