from django.urls import path

from goal.apps import GoalConfig
from goal.views import (
    GoalListAPIView,
    GoalCreateAPIView,
    GoalUpdateAPIView,
    GoalDestroyAPIView,
    GoalRetrieveAPIView, PublicGoalTemplateView, GoalCreateView, GoalListView, GoalUpdateView, GoalDetailView,
    GoalDeleteView,
)

app_name = GoalConfig.name


urlpatterns = [
    path("public/", PublicGoalTemplateView.as_view(), name="public_goal_list"),
    path("my/", GoalListView.as_view(), name="goal_list"),
    path("create/", GoalCreateView.as_view(), name="goal_create"),
    path("<int:pk>/update/", GoalUpdateView.as_view(), name="goal_update"),
    path("<int:pk>/detail/", GoalDetailView.as_view(), name="goal_detail"),
    path("<int:pk>/delete/", GoalDeleteView.as_view(), name="goal_delete"),

    path("api/moments/", PublicGoalTemplateView.as_view(), name="public_moments_api"),
    path("api/my/", GoalListAPIView.as_view(), name="moments_list_api"),
    path("api/create/", GoalCreateAPIView.as_view(), name="moments_create_api"),
    path("api/<int:pk>/update/", GoalUpdateAPIView.as_view(), name="moments_update_api"),
    path("api/<int:pk>/detail/", GoalRetrieveAPIView.as_view(), name="moments_detail_api"),
    path("api/<int:pk>/delete/", GoalDestroyAPIView.as_view(), name="moments_delete_api"),
]
