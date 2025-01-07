from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import *
from users.tests import BaseTestCase
import os

User = get_user_model()

class QuizBaseTestCase(BaseTestCase):
    """
    Base test case to prepare quizzes for testing, inheriting user setup from BaseTestCase.
    """
    @classmethod
    def setUpTestData(cls):
        # Call the parent setup to prepare users and course
        super().setUpTestData()

        # Create a quiz for the course
        cls.quiz = Quiz.objects.create(
            name="Test Quiz",
            course=cls.course1,
            lesson=cls.course1_lesson1,
            difficulty = 'easy',
            time=1,  # In minutes
            required_score = 50,
            number_of_questions =2,
        )

        # Create a couple questions(q) with answers(a) for this quiz
        cls.q1 = Question.objects.create( # Question 1
            quiz=cls.quiz,
            text = 'Question 1',
            question_order = 1,
        )

        cls.a1_1 = Answer.objects.create( # Answer 1 for Q1
            question = cls.q1,
            text = 'No',
            is_correct = False,
        )

        cls.a1_2 = Answer.objects.create( # Answer 2 for Q1
            question = cls.q1,
            text = 'Yes',
            is_correct = True,
        )

        cls.q2 = Question.objects.create( # Question 2
            quiz=cls.quiz,
            text = 'Question 2',
            question_order = 2,
        )

        cls.a2_1 = Answer.objects.create( # Answer 1 for Q2
            question = cls.q2,
            text = 'No',
            is_correct = False,
        )

        cls.a2_2 = Answer.objects.create( # Answer 2 for Q2
            question = cls.q2,
            text = 'Yes',
            is_correct = True,
        )



class TestStudentDashboardView(BaseTestCase):
    def setUp(self):
        self.dashboard_url = reverse('learning:student_dashboard')
        self.client.login(username='student1', password='password123')
        self.client.post(reverse('users:enroll', args=[self.course1.id])) # Enroll in course1

    def test_dashboard_context_data(self):
        """ Tests for whether context data contains the correct dashboard information."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        
        context = response.context
        self.assertIn('course_progress_data', context)

        # Verify data for enrolled courses
        progress_data = context['course_progress_data']
        self.assertEqual(len(progress_data), 1)  # Student enrolled in 1 course
        self.assertEqual(progress_data[0]['course'], self.course1.title)
        self.assertEqual(progress_data[0]['progress'], 0) # Must be 0 since no assignments submitted yet
        self.assertEqual(len(progress_data[0]['completed_assignments']), 0) # No submitted assignments yet
        self.assertEqual(progress_data[0]['last_accessed_lesson_order'], 1) # Must be 1 since no lessons completed yet
        

    def test_context_after_completing_lesson(self):
        """ 
        Tests submitting a file assignment for lesson and then 
        tests whether context data of student dashboard was updated and calculated correctly. 
        """
        # Simulate visiting the lesson to "complete" it 
        lesson_url = reverse('learning:lesson', kwargs={'course_title': self.course1.title, 'lesson_order': self.course1_lesson1.order})
        response = self.client.get(lesson_url)
        self.assertEqual(response.status_code, 200)

        # Get the absolute path to the test assignment file
        test_file_path = os.path.join(settings.BASE_DIR, 'media', 'assignment_files', 'Test-assignment.pdf')        
        
        # Simulate the POST request with assignment file (submitting assignment)
        with open(test_file_path, 'rb') as file:
            response = self.client.post(
                reverse('learning:lesson', kwargs={'course_title': self.course1.title, 'lesson_order': self.course1_lesson1.order}),
                {'assignment': file},
                follow=True  # Follow the redirect
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lesson Completed")
        
        # Reload the dashboard and verify the context
        response = self.client.get(self.dashboard_url)
        context = response.context

        # Verify data for enrolled courses
        progress_data = context['course_progress_data']
        self.assertEqual(progress_data[0]['progress'], 50) # Must be 50% since 1 of 2 lessons completed
        self.assertEqual(progress_data[0]['last_accessed_lesson_order'], 2) # Must be 2 after completing lesson1
        
        # Verify the assignment appears as submitted
        completed_assignments = progress_data[0]['completed_assignments']
        self.assertEqual(len(completed_assignments), 1)



class TestQuiz(QuizBaseTestCase):
    def setUp(self):
        self.client.login(username='student1', password='password123')
        self.client.post(reverse('users:enroll', args=[self.course1.id])) # Enroll in course1


    def test_quiz_start_context_data(self):
        response = self.client.get(reverse('learning:quiz_start', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(context['session_exists'], False) # Ensure that session wasn't started yet


    def test_quiz_flow(self):
        """
        Tests taking a quiz and submitting 2/2 correct quiz answers.
        """
        # First simulate a visit to QuizStart page - important step to initialize the StudentQuizSession
        response = self.client.get(reverse('learning:quiz_start', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        
        # Get the first question
        response = self.client.get(reverse('learning:quiz_question', args=[self.quiz.id, 1]))
        self.assertEqual(response.status_code, 200)
        
        # Submit correct answer, follow a redirect to the second question
        response = self.client.post(
            reverse('learning:quiz_question', kwargs={'quiz_id': self.quiz.id, 'question_order': 1}),
            # The POST method expects the data to be submitted as a dictionary under the data parameter
            data={'student_answer': self.a1_2.id},
            follow=True, # Without this line status_code would be 302 (a redirect)
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Question 2') # Ensure successful redirect to the next question
        self.assertEqual(response.context['progress_percentage'], 50.0) # Progress bar should update, since 1 of 2 questions was answered

        # Submit correct answer, follow a redirect to Quiz Complete page
        response = self.client.post(
            reverse('learning:quiz_question', kwargs={'quiz_id': self.quiz.id, 'question_order': 2}),
            data={'student_answer': self.a2_2.id},
            follow=True, 
        )
        self.assertEqual(response.status_code, 200)

        # Submitting answer to the last question of the quiz should redirect to quiz_complete page
        self.assertTemplateUsed(response, 'learning/quiz_complete.html') 
        self.assertContains(response, 'PASSED')

        # Score is 100% since 2/2 questions were answered correctly
        self.assertEqual(response.context['session'].score, 100)    