from django.contrib import admin
from .models import Feedback, Level, Lesson, Age, User, Parent, SubCoach, SubPsychologist, VerifyPhone, \
    Payment, Notification, MyPlan, Message
from .translations import CustomAdmin


@admin.register(Message)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'seen', 'created_at']


@admin.register(Notification)
class NotificationAdmin(CustomAdmin):
    list_display = ['user', 'is_read', 'created_at']


@admin.register(MyPlan)
class MyPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'percent', 'date']


@admin.register(SubPsychologist)
class PsychologicalAdmin(admin.ModelAdmin):
    list_display = ['psychologist']


@admin.register(SubCoach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ['coach']


@admin.register(VerifyPhone)
class VerifyPhoneAdmin(admin.ModelAdmin):
    list_display = ['phone', 'code']


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    filter_horizontal = ['children']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ['password', 'last_login', 'groups', 'user_permissions', 'is_superuser', 'is_staff']
    list_display = ['phone', 'id', 'name', 'role', 'created_at']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['sender', 'name', 'date']
    filter_horizontal = ['students']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']


@admin.register(Level)
class LevelAdmin(CustomAdmin):
    list_display = ['name']


@admin.register(Age)
class AgeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'ended_at']
