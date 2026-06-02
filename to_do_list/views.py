from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from .forms import SignUpForm, LogInForm, ToDoItemFormSet
from django.contrib.auth import login
from .models import ToDoList, ToDoItem, Habit, HabitRecord, HabitTrackingMonth, UserProfile
from django.views import View
from django.utils import timezone
from calendar import monthrange
from django.db.models import Prefetch, Count
from datetime import timedelta, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
from .utils import build_month_calendar

WEEKDAYS = ["M", "T", "W", "T", "F", "S", "S"]


class LogInView(LoginView):
    template_name = "auth.html"
    authentication_form = LogInForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Log In"
        return context


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "auth.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Sign Up"
        return context


class SettingsView(TemplateView):
    template_name = "settings.html"


class AboutView(TemplateView):
    template_name = "about.html"


class HomeView(View):
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        self.today = timezone.localdate()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        return super().dispatch(request, *args, **kwargs)


    def get_todo_list(self, date):
        if self.request.user.is_authenticated:
            return ToDoList.objects.filter(user=self.request.user, date=date).first()
        return None

    def get_habits(self):
        habits = (Habit.objects.filter(
            user=self.request.user,
            months_tracked__year=self.today.year,
            months_tracked__month=self.today.month
        ).prefetch_related(
            Prefetch(
                'records',
                queryset=HabitRecord.objects.filter(
                    date__year=self.today.year,
                    date__month=self.today.month)
            )
        ))
        return habits

    def get_formset_for_date(self, date, prefix, data=None):
        todo_list = self.get_todo_list(date)
        queryset = todo_list.items.all() if todo_list else ToDoItem.objects.none()
        return ToDoItemFormSet(data=data, queryset=queryset, prefix=prefix)


    def get_formset_context(self, submitted_formset=None, prefix=None):
        formsets = {
            "yesterday": self.get_formset_for_date(self.yesterday, prefix="yesterday"),
            "today": self.get_formset_for_date(self.today, prefix="today"),
            "tomorrow": self.get_formset_for_date(self.tomorrow, prefix="tomorrow")
        }

        if submitted_formset and prefix:
            formsets[prefix] = submitted_formset

        return {
            "date_yesterday": self.yesterday,
            "date_today": self.today,
            "date_tomorrow": self.tomorrow,
            "formsets": {
                self.yesterday: formsets["yesterday"],
                self.today: formsets["today"],
                self.tomorrow: formsets["tomorrow"],
            },
        }

    def get_habit_context(self):
        return {
            "habits": self.get_habits(),
        }

    def get_calendar_context(self):
        return {
            "month_date": self.today,
            "month_calendar": build_month_calendar(self.today.year, self.today.month),
            "weekdays": WEEKDAYS,
            "editable": True,
        }

    def get_context_data(self, submitted_formset=None, prefix=None):
        context = {}

        context.update(self.get_formset_context(submitted_formset=submitted_formset, prefix=prefix))
        context.update(self.get_habit_context())
        context.update(self.get_calendar_context())
        return context


    def get_submitted_formset_info(self, post_data):
        for prefix, date_obj in {
            "yesterday": self.yesterday,
            "today": self.today,
            "tomorrow": self.tomorrow,
        }.items():
            if f"{prefix}-TOTAL_FORMS" in post_data:
                return prefix, date_obj
        return None, None

    def save_formset(self, formset, date_obj):
        todo_list = self.get_todo_list(date_obj) or ToDoList.objects.create(user=self.request.user, date=date_obj)
        instances = formset.save(commit=False)
        for instance in instances:
            instance.to_do_list = todo_list
            instance.save()
        for obj in formset.deleted_objects:
            obj.delete()


    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")

        prefix, date_obj = self.get_submitted_formset_info(request.POST)
        if not prefix:
            return redirect('home')

        formset = self.get_formset_for_date(date_obj, prefix=prefix, data=request.POST)

        if formset.is_valid():
            self.save_formset(formset, date_obj)
            return redirect('home')

        return render(request, self.template_name, self.get_context_data(submitted_formset=formset, prefix=prefix))


class HistoryMenuView(LoginRequiredMixin, TemplateView):
    template_name = "history-menu.html"


class ToDoHistoryView(ListView):
    model = ToDoList
    template_name = "history-todo.html"
    context_object_name = "todo_lists"
    paginate_by = 10

    def get_queryset(self):
        return ToDoList.objects.filter(user=self.request.user).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse("history-menu")
        return context


class ToDoHistoryDetailView(DetailView):
    model = ToDoList
    context_object_name = "todo_list"
    template_name = "partials/day-readonly.html"

    def get_object(self, queryset=None):
        date_str = self.kwargs.get("date")
        date_obj = parse_date(date_str)
        return get_object_or_404(ToDoList, user=self.request.user, date=date_obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse("todo-history")
        context['editable'] = False
        return context


class HabitMonthHistoryView(ListView):
    template_name = "history-habit-month.html"
    context_object_name = "months_with_habits"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        return (
            HabitRecord.objects.filter(habit__user=user)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('-month')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse("history-menu")
        return context


class HabitMonthHistoryDetailView(TemplateView):
    template_name = "partials/month-readonly.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        month_str = self.kwargs.get('month')
        month_date = datetime.strptime(month_str, "%Y-%m").date()

        first_day = month_date.replace(day=1)
        last_day = month_date.replace(day=monthrange(month_date.year, month_date.month)[1])

        active_habits_this_month = Habit.objects.filter(
            user=user,
            records__date__range=(first_day, last_day)
        ).distinct().prefetch_related(
            Prefetch(
                'records',
                queryset=HabitRecord.objects.filter(date__gte=first_day, date__lte=last_day)
            )
        )

        context.update({
            "month_date": month_date,
            "habits": active_habits_this_month,
            "month_calendar": build_month_calendar(month_date.year, month_date.month),
            "weekdays": WEEKDAYS,
            "editable": False,
            "back_url": reverse("habit-history")

        })

        return context


class HabitCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        if name:
            habit = Habit.objects.create(user=request.user, name=name)
            today = timezone.localdate()
            HabitTrackingMonth.objects.create(
                habit=habit,
                year=today.year,
                month=today.month
            )
        return redirect("home")


class TrackHabitsView(LoginRequiredMixin, View):
    def post(self, request):
        today = timezone.localdate()
        habit_ids = request.POST.getlist("habits")
        habits = Habit.objects.filter(
            user=request.user,
            id__in=habit_ids,
        )

        for habit in habits:
            HabitTrackingMonth.objects.get_or_create(
                habit=habit,
                year=today.year,
                month=today.month
            )

        return redirect("home")


class UntrackHabitsView(LoginRequiredMixin ,View):
    def post(self, request):
        today = timezone.localdate()
        habit_ids = request.POST.getlist("habits")
        habits = Habit.objects.filter(
            user=request.user,
            id__in=habit_ids,
        )

        for habit in habits:
            HabitTrackingMonth.objects.filter(
                habit=habit,
                year=today.year,
                month=today.month
            ).delete()

        return redirect("home")
