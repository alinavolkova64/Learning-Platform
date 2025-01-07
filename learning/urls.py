from django.urls import path
from .views import *

urlpatterns = [
    path('student/dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),

    path('quizzes/', QuizListView.as_view(), name='quizzes'),
    path('quiz-start/<int:quiz_id>/', QuizStartView.as_view(), name='quiz_start'),
    path('quiz-question/<int:quiz_id>/<int:question_order>/', QuizQuestionView.as_view(), name='quiz_question'),
    path('quiz-complete/<int:quiz_id>/', QuizCompleteView.as_view(), name='quiz_complete'),
    path('quiz-finalize/<int:quiz_id>/', FinalizeQuizView.as_view(), name='quiz_finalize'),

    path('new-notifications-count/', NewNotifCount.as_view(), name="new_notif_count"),
    path('mark-notifications-read/', MarkNotificationsRead.as_view(), name="mark_notifs_read"),
    path('notifications/', Notifications.as_view(), name='notifications'),
    
    path('lesson/<str:course_title>/<int:lesson_order>/', LessonView.as_view(), name='lesson'),
]