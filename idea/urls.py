from django.urls import path

from idea.apps import MyideaConfig
from idea.views import (
    PublicIdeaListAPIView,
    IdeaListAPIView,
    IdeaCreateAPIView,
    IdeaUpdateAPIView,
    IdeaDestroyAPIView,
    IdeaRetrieveAPIView,
    PublicIdeaTemplateView,
    IdeaListView,
    IdeaCreateView,
    IdeaUpdateView,
    IdeaDetailView,
    IdeaDeleteView,
)

app_name = MyideaConfig.name

urlpatterns = [
    # HTML Views
    path("public/", PublicIdeaTemplateView.as_view(), name="public_idea_list"),
    path("my/", IdeaListView.as_view(), name="idea_list"),
    path("create/", IdeaCreateView.as_view(), name="idea_create"),
    path("<int:pk>/update/", IdeaUpdateView.as_view(), name="idea_update"),
    path("<int:pk>/detail/", IdeaDetailView.as_view(), name="idea_detail"),
    path("<int:pk>/delete/", IdeaDeleteView.as_view(), name="idea_delete"),
    # API Views
    path("api/idea/", PublicIdeaTemplateView.as_view(), name="public_idea_api"),
    path("api/my/", IdeaListAPIView.as_view(), name="idea_list_api"),
    path("api/create/", IdeaCreateAPIView.as_view(), name="idea_create_api"),
    path("api/<int:pk>/update/", IdeaUpdateAPIView.as_view(), name="idea_update_api"),
    path("api/<int:pk>/detail/", IdeaRetrieveAPIView.as_view(), name="idea_detail_api"),
    path("api/<int:pk>/delete/", IdeaDestroyAPIView.as_view(), name="idea_delete_api"),
]
