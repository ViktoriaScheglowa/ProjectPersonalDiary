from django.urls import path

from moments.apps import MomentsConfig
from moments.views import (
    PublicMomentsTemplateView,
    MomentsListAPIView,
    MomentsCreateView,
    MomentsUpdateView,
    MomentsDeleteView,
    MomentsDetailView,
    PublicMomentsTemplateView,
    MomentsCreateAPIView,
    MomentsUpdateAPIView,
    MomentsDestroyAPIView,
    MomentsRetrieveAPIView, MomentsListView,
)

app_name = MomentsConfig.name

urlpatterns = [
    # HTML Views
    path("public/", PublicMomentsTemplateView.as_view(), name="public_moments_list"),
    path("my/", MomentsListView.as_view(), name="moments_list"),
    path("create/", MomentsCreateView.as_view(), name="moments_create"),
    path("<int:pk>/update/", MomentsUpdateView.as_view(), name="moments_update"),
    path("<int:pk>/detail/", MomentsDetailView.as_view(), name="moments_detail"),
    path("<int:pk>/delete/", MomentsDeleteView.as_view(), name="moments_delete"),

    # API Views
    path("api/moments/", PublicMomentsTemplateView.as_view(), name="public_moments_api"),
    path("api/my/", MomentsListAPIView.as_view(), name="moments_list_api"),
    path("api/create/", MomentsCreateAPIView.as_view(), name="moments_create_api"),
    path("api/<int:pk>/update/", MomentsUpdateAPIView.as_view(), name="moments_update_api"),
    path("api/<int:pk>/detail/", MomentsRetrieveAPIView.as_view(), name="moments_detail_api"),
    path("api/<int:pk>/delete/", MomentsDestroyAPIView.as_view(), name="moments_delete_api"),
]