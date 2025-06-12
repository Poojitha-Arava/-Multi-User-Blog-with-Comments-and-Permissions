from django.urls import path
from .views import register, CustomLoginView, profile, custom_logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', profile, name='profile'),
]