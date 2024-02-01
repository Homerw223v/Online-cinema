from movies.api.v1.views import FilmWorkViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('movies', FilmWorkViewSet, basename='movies')

urlpatterns = router.urls
