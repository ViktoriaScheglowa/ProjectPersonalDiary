from django.urls import path

from habits.views import PublicHabitsTemplateView
from moments.apps import MomentsConfig
from moments.views import (
    PublicMomentsListAPIView,
    MomentsListAPIView,
    MomentsCreateAPIView,
    MomentsUpdateAPIView,
    MomentsDestroyAPIView,
    MomentsRetrieveAPIView,
)

app_name = MomentsConfig.name

urlpatterns = [
    path("public/", PublicHabitsTemplateView.as_view(), name="public_habits_list"),
    path("moments/", PublicMomentsListAPIView.as_view(), name="public_moments_api"),
    path("my/", MomentsListAPIView.as_view(), name="moments_list"),
    path("create/", MomentsCreateAPIView.as_view(), name="moments_create"),
    path("<int:pk>/update/", MomentsUpdateAPIView.as_view(), name="moments_update"),
    path("<int:pk>/detail/", MomentsRetrieveAPIView.as_view(), name="moments_detail"),
    path("<int:pk>/delete/", MomentsDestroyAPIView.as_view(), name="moments_delete"),
]