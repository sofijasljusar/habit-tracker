from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm, LogInForm
from django.contrib.auth import login


# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"


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
