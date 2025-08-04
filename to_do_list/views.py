from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, LogInForm, ToDoItemFormSet
from django.contrib.auth import login
import datetime
from .models import ToDoList, ToDoItem, Habit, HabitRecord
from django.views import View
from django.utils import timezone
from calendar import monthrange
from django.db.models import Prefetch
import calendar


class HomeView(View):
    template_name = "home.html"

    def get_todo_list(self, date):
        if self.request.user.is_authenticated:
            return ToDoList.objects.filter(user=self.request.user, date=date).first()
        return None

    def get_formset_for_date(self, date, prefix, data=None):
        todo_list = self.get_todo_list(date)
        queryset = todo_list.items.all() if todo_list else ToDoItem.objects.none()
        return ToDoItemFormSet(data=data, queryset=queryset, prefix=prefix)

    def dispatch(self, request, *args, **kwargs):
        self.today = timezone.localtime(timezone.now()).date()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.tomorrow = self.today + datetime.timedelta(days=1)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")

        first_day = self.today.replace(day=1)
        last_day = self.today.replace(day=monthrange(self.today.year, self.today.month)[1])
        habits = Habit.objects.filter(user=request.user).prefetch_related(
            Prefetch(
                'records',
                queryset=HabitRecord.objects.filter(date__gte=first_day, date__lte=last_day)
            )
        )
        month_calendar = []

        # Returns a matrix: each inner list represents a week (Mon = 0)
        cal = calendar.Calendar(firstweekday=0)  # 0 = Monday; change to 6 if you want Sunday start

        for week in cal.monthdayscalendar(self.today.year, self.today.month):
            month_calendar.append(week)  # week = [0 if no day, else day number]

        context = {
            "date_yesterday": self.yesterday,
            "date_today": self.today,
            "date_tomorrow": self.tomorrow,
            "formset_yesterday": self.get_formset_for_date(self.yesterday, prefix="yesterday"),
            "formset_today": self.get_formset_for_date(self.today, prefix="today"),
            "formset_tomorrow": self.get_formset_for_date(self.tomorrow, prefix="tomorrow"),
            "habits": habits,
            "month_start": first_day,
            "month_end": last_day,
            "month_calendar": month_calendar,
            "weekdays": ["M", "T", "W", "T", "S", "S"],
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")

        # Detect which formset is being submitted by checking the management form key
        if 'yesterday-TOTAL_FORMS' in request.POST:
            prefix = 'yesterday'
            date = self.yesterday
        elif 'today-TOTAL_FORMS' in request.POST:
            prefix = 'today'
            date = self.today
        elif 'tomorrow-TOTAL_FORMS' in request.POST:
            prefix = 'tomorrow'
            date = self.tomorrow
        else:
            # No formset submitted or invalid submission - reload
            return redirect('home')

        formset = self.get_formset_for_date(date, prefix=prefix, data=request.POST)

        if formset.is_valid():
            todo_list = self.get_todo_list(date)
            if not todo_list:
                todo_list = ToDoList.objects.create(user=request.user, date=date)
            instances = formset.save(commit=False)
            for instance in instances:
                instance.to_do_list = todo_list
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('home')

        # If invalid, reload formsets but replace submitted one with errors
        context = {
            "date_yesterday": self.yesterday,
            "date_today": self.today,
            "date_tomorrow": self.tomorrow,
            "formset_yesterday": self.get_formset_for_date(self.yesterday, prefix="yesterday") if prefix != "yesterday" else formset,
            "formset_today": self.get_formset_for_date(self.today, prefix="today") if prefix != "today" else formset,
            "formset_tomorrow": self.get_formset_for_date(self.tomorrow, prefix="tomorrow") if prefix != "tomorrow" else formset,
        }
        return render(request, self.template_name, context)


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


class HistoryMenuView(TemplateView):
    template_name = "history-menu.html"


class AboutView(TemplateView):
    template_name = "about.html"


class BaseDetailView(TemplateView):
    template_name = "detail-page.html"
    include_template = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["include_template"] = self.include_template
        return context


class MonthDetailView(BaseDetailView):
    include_template = "partials/month-detail.html"


class DayDetailView(BaseDetailView):
    include_template = "partials/day-detail.html"


class HabitCreateView(View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        if name:
            Habit.objects.create(user=request.user, name=name)
        return redirect("home")
