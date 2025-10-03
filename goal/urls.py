from django.urls import path

from goal.apps import GoalConfig
from goal.views import (
    PublicGoalListAPIView,
    GoalListAPIView,
    GoalCreateAPIView,
    GoalUpdateAPIView,
    GoalDestroyAPIView,
    GoalRetrieveAPIView,
)

app_name = GoalConfig.name

urlpatterns = [
    path("goal/", PublicGoalListAPIView.as_view(), name="public_goal_list"),
    path("my/", GoalListAPIView.as_view(), name="goal_list"),
    path("create/", GoalCreateAPIView.as_view(), name="goal_create"),
    path("<int:pk>/update/", GoalUpdateAPIView.as_view(), name="goal_update"),
    path("<int:pk>/detail/", GoalRetrieveAPIView.as_view(), name="goal_detail"),
    path("<int:pk>/delete/", GoalDestroyAPIView.as_view(), name="goal_delete"),
]
