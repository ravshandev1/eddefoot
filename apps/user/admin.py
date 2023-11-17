from django.contrib import admin
from .models import Feedback, Level, Lesson, Age, User, Parent, ParentControl, Coach, Psychological, VerifyPhone, \
    Payment, Notification, MyPlan
from .translations import CustomAdmin


@admin.register(Notification)
class NotificationAdmin(CustomAdmin):
    pass


@admin.register(MyPlan)
class MyPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Psychological)
class PsychologicalAdmin(admin.ModelAdmin):
    filter_horizontal = ['students']


@admin.register(VerifyPhone)
class VerifyPhoneAdmin(admin.ModelAdmin):
    list_display = ['phone', 'code']


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    filter_horizontal = ['students']


@admin.register(ParentControl)
class ParentControlAdmin(admin.ModelAdmin):
    list_display = ['user', 'time', 'created_at']


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    filter_horizontal = ['children']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ['password', 'last_login', 'groups', 'user_permissions', 'is_superuser', 'is_staff']


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
