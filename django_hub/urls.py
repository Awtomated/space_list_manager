# The host project registers its own viewsets.
# Example in your project's urls.py:
#
#   from rest_framework.routers import SimpleRouter
#   from hub.views import SpaceViewset, FolderViewset
#
#   router = SimpleRouter()
#   router.register('spaces', SpaceViewset, basename='space')
#   router.register('folders', FolderViewset, basename='folder')
#
#   urlpatterns = [path('api/hub/', include(router.urls))]

urlpatterns = []
