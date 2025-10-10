from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView, DeleteView
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
from goal.forms import GoalForms
from goal.paginators import CustomPaginator
from goal.serializers import GoalSerializer, PublicListGoalSerializer


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goal/my_goal_list.html'
    context_object_name = 'goal'
    paginate_by = 5

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForms
    template_name = 'goal/goal_form.html'
    success_url = reverse_lazy('goal:goal_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForms
    template_name = 'goal/goal_form.html'
    success_url = reverse_lazy('goal:goal_list')

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


class GoalDetailView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'goal/goal_detail.html'
    context_object_name = 'goal'

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = 'goal/goal_confirm_delete.html'
    success_url = reverse_lazy('goal:goal_list')

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


# API Views (оставляем для API)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список личных моментов",
    ),
)
class GoalListAPIView(ListAPIView):
    serializer_class = GoalSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных моментов",
    ),
)
class PublicGoalTemplateView(TemplateView):
    template_name = 'goal/public_goal_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goals = Goal.objects.filter(is_public=True)
        print(f"Found {len(goals)} public goal")  # Для отладки
        context['goals'] = goals
        return context


class GoalCreateAPIView(CreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.accepted_media_type == 'text/html' or 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            return render(request, 'goal/create_form.html')
        return super().get(request, *args, **kwargs)


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
    Доступ к конкретным целям есть только у создателя цели и суперпользователя.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def perform_update(self, serializer):
        user = self.request.user
        habit = self.get_object()

        if not user == habit.owner:
            raise PermissionDenied("У Вас нет прав редактировать эту цель.")
        serializer.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр цели",
    ),
)
class GoalRetrieveAPIView(RetrieveAPIView):
    """
    Просмотр детальной информации о цели.
    Неавторизованный пользователь может просматривать только публичные цели.
    Непубличную цель может просматривать только создатель и суперпользователь.
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
        operation_summary="Удаление момента",
    ),
)
class GoalDestroyAPIView(DestroyAPIView):
    """
    Владелец момента может удалять момент из БД.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этой цели.")

        self.perform_destroy(instance)
        return Response(status=204)
