from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    TemplateView,
    DeleteView,
    DetailView,
    UpdateView,
    CreateView,
    ListView,
)
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
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Q

from habits.forms import HabitForm
from habits.models import Habit
from habits.paginators import CustomPaginator
from habits.serializers import HabitSerializer, PublicListHabitSerializer


# HTML Views для привычек
class HabitListView(LoginRequiredMixin, ListView):
    model = Habit
    template_name = "habits/my_habits_list.html"
    context_object_name = "habits"
    paginate_by = 5

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных моментов",
    ),
)
class PublicHabitsTemplateView(TemplateView):
    template_name = "habits/public_habits_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habits = Habit.objects.filter(is_public=True)
        print(f"Found {len(habits)} public habits")  # Для отладки
        context["habits"] = habits
        return context


class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    form_class = HabitForm
    template_name = "habits/habits_form.html"
    success_url = reverse_lazy("habits:habits_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        if (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.telegram_chat_id
        ):
            form.instance.telegram_chat_id = self.request.user.profile.telegram_chat_id
            print(
                f"✅ Автоматически добавлен chat_id: {self.request.user.profile.telegram_chat_id}"
            )
        else:
            print("⚠️ У пользователя нет chat_id в профиле")
        return super().form_valid(form)


class HabitUpdateView(LoginRequiredMixin, UpdateView):
    model = Habit
    template_name = "habits/habits_form.html"
    fields = [
        "location",
        "date_deadline",
        "time_deadline",
        "action",
        "is_enjoyable",
        "associated_habit",
        "periodicity",
        "reward",
        "time_to_complete",
        "is_public",
    ]
    success_url = reverse_lazy("habits:habits_list")

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


class HabitDetailView(LoginRequiredMixin, DetailView):
    model = Habit
    template_name = "habits/habits_detail.html"
    context_object_name = "habit"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(
                models.Q(is_public=True) | models.Q(owner=self.request.user)
            )
        else:
            return Habit.objects.filter(is_public=True)


class HabitDeleteView(LoginRequiredMixin, DeleteView):
    model = Habit
    template_name = "habits/habits_confirm_delete.html"
    success_url = reverse_lazy("habits:habits_list")

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


@method_decorator(cache_page(60 * 15), name="dispatch")
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список личных привычек",
    ),
)
class HabitListAPIView(ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = cache.get(f"habits_list_{user.id}")
        if not queryset:
            queryset = Habit.objects.filter(owner=user)
            cache.set(f"habits_list_{user.id}", queryset, 60 * 15)
        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список публичных привычек",
    ),
)
class PublicHabitListAPIView(ListAPIView):
    context_object_name = "public_habits"
    serializer_class = PublicListHabitSerializer
    pagination_class = CustomPaginator
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = cache.get("public_habits_list")
        if not queryset:
            queryset = Habit.objects.filter(is_public=True)
            cache.set("public_habits_list", queryset, 60 * 15)
        return queryset


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание привычки",
    ),
)
class HabitCreateAPIView(CreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        operation_summary="Редактирование привычки",
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Частичное редактирование привычки",
    ),
)
class HabitUpdateAPIView(UpdateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def perform_update(self, serializer):
        user = self.request.user
        habit = self.get_object()

        if not user == habit.owner:
            raise PermissionDenied("У Вас нет прав редактировать эту привычку.")
        serializer.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр привычки",
    ),
)
class HabitRetrieveAPIView(RetrieveAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_object(self):
        obj = super().get_object()

        if not (obj.is_public or obj.owner == self.request.user):
            raise PermissionDenied(
                "У Вас нет прав просматривать информацию об этой привычке."
            )
        return obj


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Удаление привычки",
    ),
)
class HabitDestroyAPIView(DestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.owner:
            raise PermissionDenied("У вас нет прав на удаление этой привычки.")

        self.perform_destroy(instance)
        return Response(status=204)
