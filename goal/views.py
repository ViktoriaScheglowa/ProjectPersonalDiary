from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    DestroyAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    ListAPIView,
    CreateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from goal.models import Goal
from goal.paginators import CustomPaginator
from goal.serializers import GoalSerializer, PublicListGoalSerializer


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список целей",
    ),
)
class GoalListAPIView(ListAPIView):
    """
    Получение списка целей, созданных текущим пользователем. Требуются авторизация.
    Суперпользователь и модератор могут просматривать весь список целей.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = GoalSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Goal.objects.filter(owner=self.request.user)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных целей",
    ),
)
class PublicGoalListAPIView(ListAPIView):
    """
    Получение списка публичных целей. Доступно для всех пользователей.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = PublicListGoalSerializer
    pagination_class = CustomPaginator
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Goal.objects.filter(is_public=True)


class PublicGoalTemplateView(TemplateView):
    template_name = 'goal/public_goal_list.html'


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание цели",
    ),
)
class GoalCreateAPIView(CreateAPIView):
    """
    Создание новой цели. Требуются авторизация.
    Параллельно создается периодическая задача в зависимости от указанной периодичности цели.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        operation_summary="Редактирование цели",
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Частичное редактирование цели",
    ),
)
class GoalUpdateAPIView(UpdateAPIView):
    """
    Редактирование информации о цели.
    Доступ к конкретным целям есть только у создателя цели, модератора и суперпользователя.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def perform_update(self, serializer):
        user = self.request.user
        goal = self.get_object()

        if not user == goal.owner:
            raise PermissionDenied("У Вас нет прав редактировать эту цель.")
        serializer.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр привычки",
    ),
)
class GoalRetrieveAPIView(RetrieveAPIView):
    """
    Просмотр детальной информации о цели.
    Неавторизованный пользователь может просматривать только публичные цели.
    Непубличную целу может просматривать только создатель, модератор и суперпользователь.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def get_object(self):
        obj = super().get_object()

        if not (obj.is_public or obj.owner == self.request.user):
            raise PermissionDenied(
                "У Вас нет прав просматривать информацию об этой цели."
            )
        return obj


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Удаление цели",
    ),
)
class GoalDestroyAPIView(DestroyAPIView):
    """
    Владелец цели может удалять привычку из БД.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этой цели.")

        self.perform_destroy(instance)
        return Response(status=204)
