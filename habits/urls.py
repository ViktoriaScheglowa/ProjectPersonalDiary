from django.urls import path

from habits.apps import HabitsConfig
from habits.views import (
    PublicHabitListAPIView,
    HabitListAPIView,
    HabitCreateAPIView,
    HabitUpdateAPIView,
    HabitDestroyAPIView,
    HabitRetrieveAPIView, PublicHabitsTemplateView, HabitListView, HabitCreateView, HabitUpdateView, HabitDetailView,
    HabitDeleteView,
)

app_name = HabitsConfig.name

urlpatterns = [
    # HTML Views
    path("public/", PublicHabitsTemplateView.as_view(), name="public_habits_list"),
    path("my/", HabitListView.as_view(), name="habits_list"),
    path("create/", HabitCreateView.as_view(), name="habits_create"),
    path("<int:pk>/update/", HabitUpdateView.as_view(), name="habits_update"),
    path("<int:pk>/detail/", HabitDetailView.as_view(), name="habits_detail"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habits_delete"),

    # API Views
    path("api/habits/", PublicHabitListAPIView.as_view(), name="public_habits_api"),
    path("api/my/", HabitListAPIView.as_view(), name="habits_list_api"),
    path("api/create/", HabitCreateAPIView.as_view(), name="habits_create_api"),
    path("api/<int:pk>/update/", HabitUpdateAPIView.as_view(), name="habits_update_api"),
    path("api/<int:pk>/detail/", HabitRetrieveAPIView.as_view(), name="habits_detail_api"),
    path("api/<int:pk>/delete/", HabitDestroyAPIView.as_view(), name="habits_delete_api"),
]
