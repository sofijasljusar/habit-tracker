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
import calendar
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncMonth
import json

WEEKDAYS = ["M", "T", "W", "T", "F", "S", "S"]


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
        return [
            [date(self.today.year, self.today.month, day) if day else None for day in week]
            for week in cal.monthdayscalendar(self.today.year, self.today.month)]

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

    def get_context_data(self, submitted_formset=None, prefix=None):
        formsets = {
            "yesterday": self.get_formset_for_date(self.yesterday, prefix="yesterday"),
            "today": self.get_formset_for_date(self.today, prefix="today"),
            "tomorrow": self.get_formset_for_date(self.tomorrow, prefix="tomorrow")
        }

        # If these arguments are set - how formset containing errors
        if submitted_formset and prefix:
            formsets[prefix] = submitted_formset

        habits = self.get_habits()

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
            "month_date": self.today,
            "month_calendar": self.get_month_calendar(),
            "weekdays": WEEKDAYS,
            "editable": True,
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
            habit = Habit.objects.create(user=request.user, name=name)
            today = timezone.localtime(timezone.now()).date()
            HabitTrackingMonth.objects.create(
                habit=habit,
                year=today.year,
                month=today.month
            )
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
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return get_object_or_404(ToDoList, user=self.request.user, date=date_obj)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse("todo-history")
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

        cal = calendar.Calendar(firstweekday=0)  # Returns a matrix: each inner list represents a week (Mon = 0)
        month_calendar = [
            [date(month_date.year, month_date.month, day) if day else None for day in week]
            for week in cal.monthdayscalendar(month_date.year, month_date.month)]

        context.update({
            "month_date": month_date,
            "habits": active_habits_this_month,
            "month_calendar": month_calendar,
            "weekdays": WEEKDAYS,
            "editable": False,
            "back_url": reverse("habit-history")

        })

        return context


class SettingsView(TemplateView):
    template_name = "settings.html"


class UpdateThemeColorView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            color = data.get("theme_color")

            if color and color.startswith("#") and len(color) == 7:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.theme_color = color
                profile.save()
                return JsonResponse({"status": "ok"})
        except json.JSONDecodeError:
            pass

        return JsonResponse({"status": "error"}, status=400)


class OldHabitsModalView(View):
    def get(self, request):
        today = date.today()
        user_habits = Habit.objects.filter(user=request.user)
        tracked_this_month = HabitTrackingMonth.objects.filter(
            habit__user=request.user,
            year=today.year,
            month=today.month
        ).values_list('habit_id', flat=True)
        habits_to_track = user_habits.exclude(id__in=tracked_this_month)

        data = [{"id": habit.id, "name": habit.name} for habit in habits_to_track]
        return JsonResponse({"habits": data})

    def post(self, request):
        today = date.today()
        habit_ids = request.POST.getlist("habits")

        for habit_id in habit_ids:
            try:
                habit = Habit.objects.get(id=habit_id, user=request.user)
                HabitTrackingMonth.objects.get_or_create(
                    habit=habit,
                    year=today.year,
                    month=today.month
                )
            except Habit.DoesNotExist:
                continue

        return redirect("home")


class UntrackHabitsModalView(View):
    def get(self, request):
        today = date.today()
        user_habits = Habit.objects.filter(user=request.user)
        tracked_this_month = HabitTrackingMonth.objects.filter(
            habit__user=request.user,
            year=today.year,
            month=today.month
        ).values_list('habit_id', flat=True)
        habits_to_untrack = user_habits.filter(id__in=tracked_this_month)

        data = [{"id": habit.id, "name": habit.name} for habit in habits_to_untrack]
        print(data)
        return JsonResponse({"habits": data})

    def post(self, request):
        today = date.today()
        habit_ids = request.POST.getlist("habits")

        for habit_id in habit_ids:
            try:
                habit = Habit.objects.get(id=habit_id, user=request.user)
                HabitTrackingMonth.objects.filter(
                    habit=habit,
                    year=today.year,
                    month=today.month
                ).delete()
            except Habit.DoesNotExist:
                continue

            return redirect("home")
