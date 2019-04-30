from django.conf.urls import include, url
from django.urls import include, path
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'manage', FormViewSet, basename="manage")

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'view/<int:pk>/', DataViewSet.as_view({ 'get': 'config' })),
    path(r'data/charts/<int:pk>/', DataViewSet.as_view({ 'get': 'charts' })),
    path(r'data/export/<int:pk>/', DataViewSet.as_view({ 'get': 'export' })),
    path(r'data/destroy/<int:pk>/', DataViewSet.as_view({ 'delete': 'disableForm' })),
    path(r'data/<int:pk>/', DataViewSet.as_view({ 'get': 'list', 'post': 'create' })),
    path(r'data/<int:pk>/<int:id_item>/', DataViewSet.as_view({ 'get': 'retrieve', 'delete': 'disableItem', 'put': 'update' })),
]
