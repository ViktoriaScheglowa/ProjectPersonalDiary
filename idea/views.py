from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DeleteView, DetailView, UpdateView, CreateView, ListView
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

from idea.forms import IdeaForm
from idea.models import Myidea
from idea.paginators import CustomPaginator
from idea.serializers import IdeaSerializer, PublicListIdeaSerializer


class IdeaListView(LoginRequiredMixin, ListView):
    model = Myidea
    template_name = 'idea/my_idea_list.html'
    context_object_name = 'idea'
    paginate_by = 5

    def get_queryset(self):
        return Myidea.objects.filter(owner=self.request.user)


class PublicIdeaTemplateView(TemplateView):
    template_name = 'idea/public_idea_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ideas = Myidea.objects.filter(is_public=True)
        print(f"Found {len(ideas)} public ideas")  # Для отладки
        context['ideas'] = ideas
        return context


class IdeaCreateView(LoginRequiredMixin, CreateView):
    model = Myidea
    form_class = IdeaForm
    template_name = 'idea/idea_form.html'
    success_url = reverse_lazy('idea:idea_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class IdeaUpdateView(LoginRequiredMixin, UpdateView):
    model = Myidea
    form_class = IdeaForm
    template_name = 'idea/idea_form.html'
    success_url = reverse_lazy('idea:idea_list')

    def get_queryset(self):
        return Myidea.objects.filter(owner=self.request.user)


class IdeaDetailView(LoginRequiredMixin, DetailView):
    model = Myidea
    template_name = 'idea/idea_detail.html'
    context_object_name = 'idea'

    def get_queryset(self):
        return Myidea.objects.all()


class IdeaDeleteView(LoginRequiredMixin, DeleteView):
    model = Myidea
    template_name = 'idea/idea_confirm_delete.html'
    success_url = reverse_lazy('idea:idea_list')

    def get_queryset(self):
        return Myidea.objects.filter(owner=self.request.user)


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
