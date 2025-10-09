from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView
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

from moments.models import Moment
from moments.paginators import CustomPaginator
from moments.serializers import MomentsSerializer, PublicListMomentSerializer


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список личных моментов",
    ),
)
class MomentsListAPIView(ListAPIView):
    """
    Получение списка моментов, созданных текущим пользователем. Требуются авторизация.
    Суперпользователь и модератор могут просматривать весь список моментов.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = MomentsSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Moment.objects.filter(owner=self.request.user)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных моментов",
    ),
)
class PublicMomentsListAPIView(ListAPIView):
    """
    Получение списка публичных привычек. Доступно для всех пользователей.
    Реализована пагинация по 5 элементов на странице.
    """

    serializer_class = PublicListMomentSerializer
    pagination_class = CustomPaginator
    permission_classes = (AllowAny,)
    template_name = 'moments/public_moments_list.html'

    def get_queryset(self):
        return Moment.objects.filter(is_public=True)


class PublicMomentsTemplateView(TemplateView):
    template_name = 'moments/public_moments_list.html'


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание момента",
    ),
)
class MomentsCreateView(LoginRequiredMixin, CreateView):
    model = Moment
    template_name = 'moments/moment_form.html'  # укажите ваш шаблон
    fields = ['title', 'comments', 'photo', 'video', 'location', 'is_public']
    success_url = reverse_lazy('moments:moments_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Или модифицируйте API View для поддержки HTML
class MomentsCreateAPIView(CreateAPIView):
    queryset = Moment.objects.all()
    serializer_class = MomentsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if request.accepted_media_type == 'text/html' or 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'moments/create_form.html')
        return super().get(request, *args, **kwargs)


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        operation_summary="Редактирование момента",
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Частичное редактирование момента",
    ),
)
class MomentsUpdateAPIView(UpdateAPIView):
    """
    Редактирование информации о моменте.
    Доступ к конкретным моментам есть только у создателя момента, модератора и суперпользователя.
    """

    queryset = Moment.objects.all()
    serializer_class = MomentsSerializer

    def perform_update(self, serializer):
        user = self.request.user
        habit = self.get_object()

        if not user == habit.owner:
            raise PermissionDenied("У Вас нет прав редактировать этот момент.")
        serializer.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр момента",
    ),
)
class MomentsRetrieveAPIView(RetrieveAPIView):
    """
    Просмотр детальной информации о моменте.
    Неавторизованный пользователь может просматривать только публичные привычки.
    Непубличную привычку может просматривать только создатель, модератор и суперпользователь.
    """

    queryset = Moment.objects.all()
    serializer_class = MomentsSerializer

    def get_object(self):
        obj = super().get_object()

        if not (obj.is_public or obj.owner == self.request.user):
            raise PermissionDenied(
                "У Вас нет прав просматривать информацию об этом моменте."
            )
        return obj


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Удаление момента",
    ),
)
class MomentsDestroyAPIView(DestroyAPIView):
    """
    Владелец момента может удалять момент из БД.
    """

    queryset = Moment.objects.all()
    serializer_class = MomentsSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этого момента.")

        self.perform_destroy(instance)
        return Response(status=204)
