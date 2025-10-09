from django.urls import path

from moments.apps import MomentsConfig
from moments.views import (
    PublicMomentsListAPIView,
    MomentsListAPIView,
    MomentsCreateView,
    MomentsUpdateAPIView,
    MomentsDestroyAPIView,
    MomentsRetrieveAPIView, PublicMomentsTemplateView, MomentsCreateAPIView,
)

app_name = MomentsConfig.name

urlpatterns = [
    path("public/", PublicMomentsTemplateView.as_view(), name="public_habits_list"),
    path("moments/", PublicMomentsListAPIView.as_view(), name="public_moments_api"),
    path("my/", MomentsListAPIView.as_view(), name="moments_list"),
    path("create/", MomentsCreateView.as_view(), name="moments_create"),
path("api/create/", MomentsCreateAPIView.as_view(), name="moments_create_api"),
    path("<int:pk>/update/", MomentsUpdateAPIView.as_view(), name="moments_update"),
    path("<int:pk>/detail/", MomentsRetrieveAPIView.as_view(), name="moments_detail"),
    path("<int:pk>/delete/", MomentsDestroyAPIView.as_view(), name="moments_delete"),
]