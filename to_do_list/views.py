from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, LogInForm, ToDoItemFormSet
from django.contrib.auth import login
import datetime
from .models import ToDoList, ToDoItem
from django.views import View


# Create your views here.
class HomeView(View):
    template_name = "home.html"

    def get_todo_list(self):
        if self.request.user.is_authenticated:
            return ToDoList.objects.filter(user=self.request.user, date=self.today).first()
        return None

    def render_form(self, formset):
        context = {
            "formset": formset,
            "todo_list": self.get_todo_list(),
            "date": self.today,
        }
        return render(self.request, self.template_name, context)

    def get_queryset(self):
        todo_list = self.get_todo_list()
        if todo_list:
            return todo_list.items.all()
        else:
            return ToDoItem.objects.none()

    def dispatch(self, request, *args, **kwargs):
        self.today = datetime.date.today()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "welcome.html")

        queryset = self.get_queryset()
        print("Number of items in queryset:", queryset.count())
        formset = ToDoItemFormSet(queryset=queryset)
        print("Number of forms in formset:", len(formset.forms))
        return self.render_form(formset)

    def post(self, request, *args, **kwargs):
        todo_list = self.get_todo_list()
        queryset = self.get_queryset()
        formset = ToDoItemFormSet(request.POST, queryset=queryset)

        if formset.is_valid():
            for f in formset.forms:
                print("Form cleaned_data:", f.cleaned_data)
            # filter input for all forms in formset (exclude invalid and deleted)
            new_items = [f for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
            print(f"Forms to save (excluding deleted): {len(new_items)}")
            if new_items and not todo_list:
                todo_list = ToDoList.objects.create(user=self.request.user, date=self.today)

            instances = formset.save(commit=False)
            for instance in instances:
                instance.to_do_list = todo_list
                instance.save()
                print(instance, "saved")
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect("home")
        print("Formset not valid")
        print(formset.errors)
        return self.render_form(formset)  # not redirect so that errors are saved in formset


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
