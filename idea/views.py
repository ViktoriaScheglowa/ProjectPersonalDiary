from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    ListAPIView,
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    CreateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from idea.models import Myidea
from idea.paginators import CustomPaginator
from idea.serializers import IdeaSerializer, PublicListIdeaSerializer


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список личных мыслей",
    ),
)
class IdeaListAPIView(ListAPIView):
    """
    Получение списка мыслей, созданных текущим пользователем. Требуются авторизация.
    Суперпользователь и модератор могут просматривать весь список мыслей.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = IdeaSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Myidea.objects.filter(owner=self.request.user)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных мыслей",
    ),
)
class PublicIdeaListAPIView(ListAPIView):
    """
    Получение списка публичных мыслей. Доступно для всех пользователей.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = PublicListIdeaSerializer
    pagination_class = CustomPaginator
    permission_classes = (AllowAny,)
    template_name = 'idea/public_idea_list.html'

    def get_queryset(self):
        return Myidea.objects.filter(is_public=True)


class PublicIdeaTemplateView(TemplateView):
    template_name = 'idea/public_idea_list.html'


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание мысли",
    ),
)
class IdeaCreateAPIView(CreateAPIView):
    """
    Создание новой мысли. Требуются авторизация.
    """

    queryset = Myidea.objects.all()
    serializer_class = IdeaSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        operation_summary="Редактирование мысли",
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Частичное редактирование мысли",
    ),
)
class IdeaUpdateAPIView(UpdateAPIView):
    """
    Редактирование информации о мысли.
    Доступ к конкретным мыслям есть только у создателя мысли, модератора и суперпользователя.
    """

    queryset = Myidea.objects.all()
    serializer_class = IdeaSerializer

    def perform_update(self, serializer):
        user = self.request.user
        habit = self.get_object()

        if not user == habit.owner:
            raise PermissionDenied("У Вас нет прав редактировать эту мысль.")
        serializer.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр мысли",
    ),
)
class IdeaRetrieveAPIView(RetrieveAPIView):
    """
    Просмотр детальной информации о мысли.
    Неавторизованный пользователь может просматривать только публичные мысли.
    Непубличную мысль может просматривать только создатель, модератор и суперпользователь.
    """

    queryset = Myidea.objects.all()
    serializer_class = IdeaSerializer

    def get_object(self):
        obj = super().get_object()

        if not (obj.is_public or obj.owner == self.request.user):
            raise PermissionDenied(
                "У Вас нет прав просматривать информацию об этой мысли."
            )
        return obj


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Удаление мысли",
    ),
)
class IdeaDestroyAPIView(DestroyAPIView):
    """
    Владелец мысли может удалять мысль из БД.
    """

    queryset = Myidea.objects.all()
    serializer_class = IdeaSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этой мысли.")

        self.perform_destroy(instance)
        return Response(status=204)
