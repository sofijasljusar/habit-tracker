from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, LogInForm, ToDoItemFormSet
from django.contrib.auth import login
from .models import ToDoList, ToDoItem, Habit, HabitRecord
from django.views import View
from django.utils import timezone
from calendar import monthrange
from django.db.models import Prefetch, Count
import calendar
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncMonth


class HomeView(View):
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        self.today = timezone.localtime(timezone.now()).date()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        return super().dispatch(request, *args, **kwargs)

    def get_todo_list(self, date):
        if self.request.user.is_authenticated:
            return ToDoList.objects.filter(user=self.request.user, date=date).first()
        return None

    def get_formset_for_date(self, date, prefix, data=None):
        todo_list = self.get_todo_list(date)
        queryset = todo_list.items.all() if todo_list else ToDoItem.objects.none()
        return ToDoItemFormSet(data=data, queryset=queryset, prefix=prefix)

    def get_month_calendar(self):
        cal = calendar.Calendar(firstweekday=0)  # Returns a matrix: each inner list represents a week (Mon = 0)
        print(cal)
        return [
            [date(self.today.year, self.today.month, day) if day else None for day in week]
            for week in cal.monthdayscalendar(self.today.year, self.today.month)]

    def get_habits(self):
        first_day = self.today.replace(day=1)
        last_day = self.today.replace(day=monthrange(self.today.year, self.today.month)[1])
        habits = Habit.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                'records',
                queryset=HabitRecord.objects.filter(date__gte=first_day, date__lte=last_day)
            )
        )
        return habits, first_day, last_day

    def get_context_data(self, submitted_formset=None, prefix=None):
        formsets = {
            "yesterday": self.get_formset_for_date(self.yesterday, prefix="yesterday"),
            "today": self.get_formset_for_date(self.today, prefix="today"),
            "tomorrow": self.get_formset_for_date(self.tomorrow, prefix="tomorrow")
        }

        # If these arguments are set - how formset containing errors
        if submitted_formset and prefix:
            formsets[prefix] = submitted_formset

        habits, month_start, month_end = self.get_habits()

        return {
            "date_yesterday": self.yesterday,
            "date_today": self.today,
            "date_tomorrow": self.tomorrow,
            "formsets": {
                self.yesterday: formsets["yesterday"],
                self.today: formsets["today"],
                self.tomorrow: formsets["tomorrow"],
            },
            "habits": habits,
            "month_start": month_start,
            "month_end": month_end,
            "month_calendar": self.get_month_calendar(),
            "weekdays": ["M", "T", "W", "T", "F", "S", "S"],
        }

    def get_form_prefix_and_date(self, post_data):
        for prefix, date_obj in {
            "yesterday": self.yesterday,
            "today": self.today,
            "tomorrow": self.tomorrow,
        }.items():
            if f"{prefix}-TOTAL_FORMS" in post_data:
                return prefix, date_obj
        return None, None

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")

        # Detect which formset is being submitted by checking the management form key
        prefix, date_obj = self.get_form_prefix_and_date(request.POST)
        if not prefix:
            return redirect('home')

        formset = self.get_formset_for_date(date_obj, prefix=prefix, data=request.POST)

        if formset.is_valid():
            todo_list = self.get_todo_list(date_obj) or ToDoList.objects.create(user=request.user, date=date_obj)
            instances = formset.save(commit=False)
            for instance in instances:
                instance.to_do_list = todo_list
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('home')

        # If invalid, reload formsets but replace submitted one with errors
        return render(request, self.template_name, self.get_context_data(submitted_formset=formset, prefix=prefix))


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


class HistoryMenuView(LoginRequiredMixin, TemplateView):
    template_name = "history-menu.html"


class AboutView(TemplateView):
    template_name = "about.html"


class BaseDetailView(LoginRequiredMixin, DetailView):
    template_name = "detail-page.html"
    include_template = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["include_template"] = self.include_template
        return context


class HabitCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        if name:
            Habit.objects.create(user=request.user, name=name)
        return redirect("home")


class HabitRecordToggleView(LoginRequiredMixin, View):
    def post(self, request, habit_id, year, month, day):
        try:
            habit = Habit.objects.get(id=habit_id, user=request.user)
        except Habit.DoesNotExist:
            return JsonResponse({"error": "Habit not found"}, status=404)

        habit_date = date(year, month, day)
        record, created = HabitRecord.objects.get_or_create(habit=habit, date=habit_date)

        if not created:
            record.delete()
            return JsonResponse({"status": "deleted"})
        return JsonResponse({"status": "created"})


class ToDoHistoryView(ListView):
    model = ToDoList
    template_name = "history-todo.html"
    context_object_name = "todo_lists"
    paginate_by = 10

    def get_queryset(self):
        return ToDoList.objects.filter(user=self.request.user).order_by("-date")


class ToDoHistoryDetailView(DetailView):
    model = ToDoList
    context_object_name = "todo_list"
    template_name = "partials/day-readonly.html"

    def get_object(self, queryset=None):
        date_str = self.kwargs.get("date")
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return get_object_or_404(ToDoList, user=self.request.user, date=date_obj)


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
