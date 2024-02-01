from movies.models import FilmWork
from rest_framework import serializers


class FilmWorkSerializer(serializers.ModelSerializer):
    """Film work serializer."""

    genres = serializers.ListField()
    actors = serializers.ListField()
    directors = serializers.ListField()
    writers = serializers.ListField()

    class Meta:
        model = FilmWork
        fields = (
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            'genres',
            'actors',
            'directors',
            'writers',
        )
