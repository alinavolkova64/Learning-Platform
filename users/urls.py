from django.urls import path
from users.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', homepage_view, name="homepage"),
    path('accounts/login/', login_view, name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('register/', register, name="register"),
    path('courses/', courses, name='courses'),
    path('course_details/<int:course_id>/', course_details, name="course_details"),
    path('enroll/<int:course_id>/', enroll, name="enroll"),
]