from .models import *
from .serializers import *
from rest_framework import generics, permissions, viewsets

class SaveIdUserMixin(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(updated_by=self.request.user)

    class Meta:
        abstract = True