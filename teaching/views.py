from rest_framework import viewsets
from users.models import Course, Lesson
from .serializers import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from learning.views import RoleRequiredMixin
from django.views.generic import TemplateView, UpdateView, View, DeleteView
from django.urls import reverse_lazy
from users.models import Course, StudentAssignment
from django.shortcuts import render, redirect
from django.db.models import Count
from .forms import *
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.views.generic.edit import FormMixin
from users.utils import send_notification

class InstructorDashboardView(TemplateView, RoleRequiredMixin):
    """
    Displays the instructor's dashboard with an overview of their courses, 
    including the number of students enrolled and assignment progress.
    """
    template_name = 'teaching/instructor_dashboard.html'
    required_role = 'instructor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all courses taught by the logged-in instructor
        instructor = self.request.user
        # Annotating courses with the number of enrollments
        courses_info = Course.objects.filter(instructor=instructor).annotate(
            students_enrolled=Count('enrollments')  # Count the enrollments for each course
        )

        # Build course-progress data with assignments
        course_progress_data = []
        for course in courses_info:
            ungraded_assignments = StudentAssignment.objects.filter(
                course=course, grade__isnull=True
            ).order_by("-date_handed_in")  # Sort newest first

            graded_assignments = StudentAssignment.objects.filter(
                course=course, grade__isnull=False
            ).order_by("-date_handed_in")  # Sort newest first

            course_progress_data.append({
                "id": course.id,
                "title": course.title,
                "ungraded_assignments": ungraded_assignments,
                "graded_assignments": graded_assignments,
            })

        context["course_progress_data"] = course_progress_data

        context["courses_info"] = [
            {
            "course": course,
            "students_enrolled": course.students_enrolled,
            } 
            for course in courses_info
        ]
        
        return context
    

#- COURSE - MANAGING - RELATED ---------------------------------------------------------------------

class CreateCourseView(TemplateView, RoleRequiredMixin, FormMixin):
    """
    Handles the creation of new courses by instructors.
    """
    template_name = 'teaching/new_course.html'
    form_class = CourseForm
    required_role = 'instructor'

    def get_success_url(self):
        return reverse_lazy("teaching:instructor_dashboard")


class CourseEditView(TemplateView, RoleRequiredMixin, FormMixin):
    """
    Allows instructors to edit details of an existing course and view its associated lessons.
    """
    template_name = 'teaching/course_edit.html'
    form_class = CourseForm
    required_role = 'instructor'

    def get_context_data(self, **kwargs):
        course_id = kwargs['pk']  # Get course ID from URL
        course = Course.objects.get(pk=course_id)
        form = CourseForm(instance=course)  # Prepopulate the form with the existing course data
        context = {
            'course': course,
            'lessons': Lesson.objects.filter(course=course).order_by("order"),  # Fetch related lessons
            'form': form,
        }
        return context
    

class CourseViewSet(viewsets.ModelViewSet, RoleRequiredMixin):
    """
    API endpoints for managing courses, including creating and updating courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    required_role = 'instructor'

    @action(detail=False, methods=['post'], url_path='create_course')
    def create_course(self, request, *args, **kwargs):
        """
        Handles the creation of a new course through the API.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(instructor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['put'], url_path='save_course_changes')
    def save_course_changes(self, request, *args, **kwargs):
        """
        Updates an existing course's details via the API.
        """
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            # Log the errors to check why it isn't saving
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#------------------------------------------------------------------------------------------



#- LESSON - MANAGING - RELATED ---------------------------------------------------------------------
class AddLessonView(TemplateView, RoleRequiredMixin, FormMixin):
    """
    Allows instructors to add a new lesson to a course, ensuring 
    the lesson order is unique within the course.
    """
    template_name = 'teaching/new_lesson.html'
    form_class = LessonForm
    required_role = 'instructor'

    def post(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        form = self.get_form()
        form.instance.course = Course.objects.get(id=course_id)

        if form.is_valid():
            # Check if the order already exists for the given course
            order_value = form.data.get('order')
            if Lesson.objects.filter(course=course_id, order=order_value).exists():
                return render(request, "teaching/new_lesson.html", 
                              {"form": form, 
                               "message": "Lesson with this order already exists."})
            else:
                form.save() 
                return redirect("teaching:edit_course", pk=course_id)

        return self.render_to_response(self.get_context_data(form=form))
    

class LessonEditView(UpdateView):
    """
    Enables instructors to edit the details of a specific lesson.
    """
    model = Lesson
    form_class = LessonForm
    template_name = "teaching/lesson_edit.html"
    context_object_name = "lesson"

    def get_success_url(self):
        return reverse_lazy("teaching:edit_course", kwargs={"pk": self.object.course.pk})


class DeleteLessonView(DeleteView, RoleRequiredMixin):
    """
    Handles the deletion of a lesson and redirects to the course 
    edit page after successful deletion.
    """
    model = Lesson
    template_name = "teaching/confirm_delete.html"
    success_url = reverse_lazy("teaching:edit_course")
    required_role = 'instructor'

    def get_success_url(self):
        messages.success(self.request, "Lesson deleted successfully!")
        return reverse_lazy("teaching:edit_course", kwargs={"pk": self.object.course.id})

#------------------------------------------------------------------------------------



class StudentAssignmentViewSet(viewsets.ModelViewSet, RoleRequiredMixin):
    """
    API endpoints for managing student assignments, including grading functionality.
    """
    queryset = StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer
    required_role = 'instructor'

    @action(detail=True, methods=['patch'], url_path='grade')
    def grade(self, request, pk=None):
        """
        Allows instructors to assign a grade to a student's assignment, 
        ensuring the grade is valid.
        """
        student_assignment = self.get_object()
        grade = request.data.get('grade')
        
        if 0 <= int(grade) <= 10:
            student_assignment.grade = grade
            student_assignment.save()
            return Response({'status': 'grade updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid grade'}, status=status.HTTP_400_BAD_REQUEST)
        

@require_GET
def get_assignment_file(request, pk):
    """
    Handles the retrieval of a file URL for a given assignment.
    """
    assignment = get_object_or_404(StudentAssignment, pk=pk)
    if not assignment.file:
        return JsonResponse({"error": "No file found for this assignment"}, status=404)
    return JsonResponse({"file_url": assignment.file.url})


class CreateAnnouncementView(RoleRequiredMixin, View):
    """
    Handles the creation of announcements for all students or students of a specific course.
    """
    required_role = 'instructor'

    def post(self, request):
        # Extract data from POST request
        recipient_option = request.POST.get("recipients")  # Either 'all' or a course's id
        message = request.POST.get("message")

        try:
            # Determine recipients
            if recipient_option == "all":
                # Get all courses taught by the instructor
                courses_taught = Course.objects.filter(instructor=request.user)
                recipients = Profile.objects.filter(enrollments__course__in=courses_taught).distinct()
            else:
                # Get profiles of students enrolled in a specific course
                course = get_object_or_404(Course, id=recipient_option, instructor=request.user)
                recipients = Profile.objects.filter(enrollments__course=course)

            # Create and send the notification
            notification = Notification.objects.create(
                sender=request.user.profile,
                message=message,
            )
            notification.recipient.add(*recipients)
            notification.save()

            send_notification(notification)  # WebSocket broadcast

            return JsonResponse({"success": True, "message": "Announcement sent successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    