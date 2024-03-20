from rest_framework import routers
from .views import VideoItemViewSet

router = routers.DefaultRouter()
router.register(r'videos', VideoItemViewSet)

urlpatterns = router.urls