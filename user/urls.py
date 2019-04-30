from .views import *
from django.urls import include, path
from django.conf.urls import include, url
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'account', UserViewSet, basename="account")
router.register(r'group', GroupViewSet, basename="group")
# router.register(r'profile', ProfileViewSet, basename="profile")
router.register(r'permission', PermissionViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    url(r'active_directory/check', user),
    path(r'profile/', ProfileViewSet.as_view({ 'get': 'retrieve', 'put': 'update' })),
]

