from django.contrib import admin
from .models import Modul, Theme, Rate, Exercise, PriceOfSubscribe
from .translations import CustomAdmin, StackAdmin


@admin.register(PriceOfSubscribe)
class PriceOfSubscribeAdmin(admin.ModelAdmin):
    list_display = ['price']


class ExerciseAdmin(StackAdmin):
    model = Exercise
    extra = 0


@admin.register(Theme)
class ThemeAdmin(CustomAdmin):
    inlines = [ExerciseAdmin]


class ModulAdmin(StackAdmin):
    model = Modul
    extra = 0


@admin.register(Rate)
class RateAdmin(CustomAdmin):
    inlines = [ModulAdmin]
