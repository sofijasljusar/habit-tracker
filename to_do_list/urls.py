from django.urls import path
from .views import HomeView, SignUpView, LogInView, HistoryMenuView, AboutView
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('history/', HistoryMenuView.as_view(), name='history-menu'),
    path('about/', AboutView.as_view(), name='about'),

]
