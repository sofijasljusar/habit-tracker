from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ToDoItem


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "input100", "placeholder": "Username"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "input100", "placeholder": "Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input100", "placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input100", "placeholder": "Confirm Password"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LogInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "input100", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "input100", "placeholder": "Password"}))


class ToDoItemForm(forms.ModelForm):
    class Meta:
        model = ToDoItem
        fields = ["title", "completed"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "title-input"}),
            "completed": forms.CheckboxInput(attrs={"class": "d-done"}),
        }


ToDoItemFormSet = forms.modelformset_factory(
    ToDoItem,
    form=ToDoItemForm,
    extra=1,
    can_delete=True
)
