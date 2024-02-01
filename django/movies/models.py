import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FilmWork(UUIDMixin, TimeStampedMixin):
    type_choices = (
        ('movie', _('Movie')),
        ('tv_show', _('TV show')),
    )

    title = models.CharField(_('title'))
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('premiere date'))
    rating = models.FloatField(
        _('rating'),
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )
    type = models.CharField(_('type'), choices=type_choices)
    genres = models.ManyToManyField('Genre', through='GenreFilmWork')
    persons = models.ManyToManyField('Person', through='PersonFilmWork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')
        indexes = [
            models.Index(
                fields=('-creation_date',),
                name='film_work_creation_date_idx',
            ),
        ]

    def __str__(self):
        return self.title


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('genre_name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        indexes = [
            models.Index(fields=('name',), name='genre_name_idx'),
        ]

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        indexes = [
            models.Index(fields=('full_name',), name='person_full_name_idx'),
        ]

    def __str__(self):
        return self.full_name


class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, verbose_name=_('filmwork'),)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_('genres'),)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name_plural = _('genre\'s filmwork')
        indexes = [
            models.Index(fields=('film_work', 'genre'), name='film_work_genre_idx'),
        ]

    def __str__(self):
        return f'{self.film_work}-{self.genre}'


class PersonFilmWork(UUIDMixin):
    type_choices = (
        ('actor', _('Actor')),
        ('writer', _('Writer')),
        ('director', _('Director')),
    )
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE, verbose_name=_('filmwork'),)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('persons'),)
    role = models.CharField(_('role'), choices=type_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name_plural = _('person\'s filmwork')
        indexes = [
            models.Index(
                fields=('film_work', 'person', 'role'),
                name='film_work_person_idx',
            ),
        ]

    def __str__(self):
        return f'{self.person}-{self.film_work}'
