from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'student-assignments', StudentAssignmentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # Include all router URLs under "api/"
    path('instructor/dashboard/', InstructorDashboardView.as_view(), name='instructor_dashboard'), 
    path('edit-course/<int:pk>/', CourseEditView.as_view(), name="edit_course"),
    path('edit-lesson/<int:pk>/', LessonEditView.as_view(), name="edit_lesson"),
    path('create-course/', CreateCourseView.as_view(), name='create_course'),
    path('add-lesson/<int:pk>/', AddLessonView.as_view(), name='add_lesson'), # Using pk of a course we're adding a lesson to
    path('lesson/<int:pk>/delete/', DeleteLessonView.as_view(), name='lesson_delete'), # Using pk of a lesson to delete

    path('assignment/<int:pk>/file/', get_assignment_file, name='get_assignment_file'),
    path('create-announcement/', CreateAnnouncementView.as_view(), name='create_announcement'),

]