from modeltranslation.translator import register, TranslationOptions
from .models import Rate, Exercise, Theme, Modul
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline


class CustomAdmin(TranslationAdmin):
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


class StackAdmin(TranslationStackedInline):
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js',
            'modeltranslation/js/tabbed_translation_fields.js',
        )
        css = {
            'screen': ('modeltranslation/css/tabbed_translation_fields.css',),
        }


@register(Modul)
class Translation(TranslationOptions):
    fields = ['name']


@register(Theme)
class Translation(TranslationOptions):
    fields = ['name']


@register(Exercise)
class Translation(TranslationOptions):
    fields = ['name', 'description']


@register(Rate)
class Translation(TranslationOptions):
    fields = ['description']
