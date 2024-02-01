from movies.api.v1.paginations import MoviesApiPagination
from movies.api.v1.serializers import FilmWorkSerializer
from movies.models import FilmWork
from rest_framework import viewsets

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q


class FilmWorkViewSet(viewsets.ModelViewSet):
    queryset = FilmWork.objects.values(
        'id',
        'title',
        'description',
        'creation_date',
        'rating',
        'type',
    )
    serializer_class = FilmWorkSerializer
    http_method_names = ['get']
    pagination_class = MoviesApiPagination

    def get_queryset(self):
        genres = ArrayAgg('genres__name', distinct=True)
        actors = ArrayAgg('persons__full_name', distinct=True, filter=Q(personfilmwork__role='actor'))
        writers = ArrayAgg('persons__full_name', distinct=True, filter=Q(personfilmwork__role='writer'))
        directors = ArrayAgg('persons__full_name', distinct=True, filter=Q(personfilmwork__role__exact='director'))
        return self.queryset.annotate(genres=genres, actors=actors, writers=writers, directors=directors)
