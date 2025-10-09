from django.urls import path

from idea.apps import MyideaConfig
from idea.views import (
    PublicIdeaListAPIView,
    IdeaListAPIView,
    IdeaCreateAPIView,
    IdeaUpdateAPIView,
    IdeaDestroyAPIView,
    IdeaRetrieveAPIView, PublicIdeaTemplateView,
)

app_name = MyideaConfig.name

urlpatterns = [
    path("public/", PublicIdeaTemplateView.as_view(), name="public_idea_list"),
    path("idea/", PublicIdeaListAPIView.as_view(), name="public_idea_api"),
    path("my/", IdeaListAPIView.as_view(), name="idea_list"),
    path("create/", IdeaCreateAPIView.as_view(), name="idea_create"),
    path("<int:pk>/update/", IdeaUpdateAPIView.as_view(), name="idea_update"),
    path("<int:pk>/detail/", IdeaRetrieveAPIView.as_view(), name="idea_detail"),
    path("<int:pk>/delete/", IdeaDestroyAPIView.as_view(), name="idea_delete"),
]
