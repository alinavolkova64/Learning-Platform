from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.db import IntegrityError
from django.db.utils import DatabaseError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from .forms import RegistrationForm, CourseFilterForm
from .models import User, Profile, Course, Lesson, Enrollment


def homepage_view(request):
    """
    View displays the main page (homepage) of the platform.
    """
    courses = Course.objects.all()
    return render(request, "users/homepage.html", {
        'courses': courses,
    })

def login_view(request):
    """
    Displays the login page and handles user authentication.

    If the request method is POST, attempts to authenticate the user. 
    If authentication is successful, the user is logged in and redirected to the homepage page. 
    If authentication fails, an error message is displayed on the login page.
    """
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            print(user)
            return HttpResponseRedirect(reverse("users:homepage"))
        else:
            return render(request, "users/login.html", {
                "message": "Invalid username and/or password."
            })
        
    # Handling other methods
    else:
        return render(request, "users/login.html")
    

@login_required
def logout_view(request):
    """
    Logs out the current user and redirects to the homepage.
    """
    logout(request)
    redirect("users:homepage")


def register(request):
    """
    Displays the registration form and handles user registration.
    """
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = RegistrationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data 
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            try:
                # Create and save user (using create_user to hash the password)
                user = User.objects.create_user(username=username, password=password, email=email, 
                                                first_name=first_name, last_name=last_name, is_superuser=False)

                # Then create and save a profile for that user
                Profile.objects.create(user=user, role=role)

                login(request, user)
                return HttpResponseRedirect(reverse(('users:homepage')))
            
            except IntegrityError:
                return render(request, "users/register.html", 
                              {"form": form, 
                               "message": "User with such username already exists."})

    # Show a blank form for the GET method
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def courses(request):
    """
    View displays a page of all courses, and offers filtering them by level and/or field of study.
    """
    form = CourseFilterForm(request.GET or None)  # Get data from the request

    courses = Course.objects.all()  # Make all courses a default

    if form.is_valid():
        levels = form.cleaned_data.get('level')
        field_of_study = form.cleaned_data.get('field_of_study')

        if levels:
            courses = courses.filter(level__in=levels)  # Filter by levels

        if field_of_study:
            courses = courses.filter(field_of_study__in=field_of_study)  # Filter by field of study

    return render(request, 'users/courses.html', {'form': form, 'courses': courses})


def course_details(request, course_id):
    """
    Displays the page of course's details, 
    including student's progress and ability to enroll.
    """
    course = Course.objects.get(id=course_id)
    lessons = course.lessons.all() # Access using related name
    

    # Check if the student is enrolled
    if request.user.profile:
        is_enrolled = Enrollment.objects.filter(student=request.user.profile, course=course).exists()
        
    progress = 0

    if is_enrolled: 
        enrollment = Enrollment.objects.get(student=request.user.profile, course=course)
        progress = enrollment.calculate_progress()

    return render(request, "users/course_details.html", {
        'course': course,
        'lessons': lessons,         
        'is_enrolled': is_enrolled, 
        'progress': progress,
    })


@login_required
def enroll(request, course_id):
    """
    View responsible for enrolling the student in the course.

    - If enrollment is successful, it returns a JSON response with success: true.
    - JavaScript handles the actual redirection to the first lesson.
    - In case of errors, it returns a JSON response with success: false and an error message.
    """
    # Get course and student profile
    course = get_object_or_404(Course, id=course_id)
    new_student = get_object_or_404(Profile, user=request.user)

    # Check if the student is already enrolled
    is_enrolled = Enrollment.objects.filter(student=new_student, course=course).exists()

    if request.method == "POST":
        # Check if the user has a student role
        if new_student.role == "student":
            if not is_enrolled:
                try:
                    # Enroll the student and fetch the first lesson
                    Enrollment.objects.create(student=new_student, course=course)
                    return JsonResponse({"success": True})
                except (DatabaseError, ObjectDoesNotExist):
                    return JsonResponse({"success": False, "message": "An error while enrolling occurred. Please try again later."})
