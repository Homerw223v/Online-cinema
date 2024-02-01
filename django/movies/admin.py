from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    autocomplete_fields = ('genre', 'film_work')
    verbose_name = _('genre_film_work_inline')
    verbose_name_plural = _('genre_film_work_inlines')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('film_work', 'genre')


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ('person', 'film_work')
    verbose_name = _('person_film_work_inline')
    verbose_name_plural = _('person_film_work_inlines')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('film_work', 'person')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 25
    ordering = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('full_name',)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'creation_date', 'rating', 'type')
    list_display = ('title', 'type', 'creation_date', 'rating')
    list_filter = ('type',)
    ordering = ('title', 'rating')
    list_editable = ('type', 'rating')
    search_fields = ('title', 'description', 'id')
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('persons', 'genres')
