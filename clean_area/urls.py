# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'waste_bins'

router = DefaultRouter()
router.register(r'districts', views.DistrictViewSet)
router.register(r'neighborhoods', views.NeighborhoodViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'bins', views.BinViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bin-status-update/', views.bin_status_update, name='bin-status-update'),
    path('statistics/', views.statistics, name='statistics'),
]