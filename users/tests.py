from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import *

User = get_user_model()

class BaseTestCase(TestCase):
    """
    Base test case to prepare users (student and instructor) and a course for testing.
    """
    @classmethod
    def setUpTestData(cls):
        # Shared setup for all tests
        cls.field_of_study1 = FieldOfStudy.objects.create(name="Data Science")
        cls.field_of_study2 = FieldOfStudy.objects.create(name="Math")

        # Create instructor and profile
        cls.instructor_user = User.objects.create_user(
            username='instructor1',
            password='password123',
            email='instructor1@example.com'
        )
        cls.instructor_profile = Profile.objects.create(
            user=cls.instructor_user,
            role='instructor'
        )

        # Create student and profile
        cls.student_user = User.objects.create_user(
            username='student1',
            password='password123',
            email='student1@example.com'
        )
        cls.student_profile = Profile.objects.create(
            user=cls.student_user,
            role='student'
        )

        # Create Data Science course
        cls.course1 = Course.objects.create(
            title="Course 1",
            level="beginner",
            instructor=cls.instructor_user,
            field_of_study = cls.field_of_study1,
        )

        # Add lessons to Course 1
        cls.course1_lesson1 = Lesson.objects.create(course=cls.course1, title="Lesson 1", order=1, content="Test 1")
        cls.course1_lesson2 = Lesson.objects.create(course=cls.course1, title="Lesson 2", order=2, content="Test 2")


        # Create Math course
        cls.course2 = Course.objects.create(
            title="Course 2",
            level="advanced",
            instructor=cls.instructor_user,
            field_of_study = cls.field_of_study2,

        )


class UserRegistrationTests(TestCase):
    """ Registration related tests. """
    def test_registration_success(self):
        response = self.client.post(reverse('users:register'), {
            'username': 'testuser',
            'first_name': 'test',
            'last_name': 'user',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'student',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect on success
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Profile.objects.filter(role='student').exists()) # Profile should be created on registration as well

    def test_registration_invalid_data(self):
        response = self.client.post(reverse('users:register'), {
            'username': '',
            'email': 'invalidemail',
            'password': '123',
            'confirm_password': '1234',
        })
        self.assertEqual(response.status_code, 200)  # Expect the form to be re-rendered


class UserLoginTest(BaseTestCase):
    """ Logging-in related tests. """
    def test_login_success(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'student1',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect on success

    def test_login_invalid_data(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'fakeuser',
            'password': 'fakepassword',
        })
        self.assertEqual(response.status_code, 200) # Expect the form to be re-rendered

    def test_logout_success(self):
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302) # Expect redirect to the homepage
        
        # Try to get the page that only authenticated user can see
        response2 = self.client.get(reverse('learning:student_dashboard')) 
        self.assertEqual(response2.status_code, 302) # Expect redirect to the login page



class CoursesViewTests(BaseTestCase):
    """ General Courses page and its filters related tests. """
    def test_courses_page_loads(self):
        response = self.client.get(reverse('users:courses'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/courses.html')
        self.assertContains(response, "Course 1")
        self.assertContains(response, "Course 2")

    def test_filter_courses_by_level(self):
        response = self.client.get(reverse('users:courses') + '?level=advanced')
        self.assertContains(response, "Course 2")
        self.assertNotContains(response, "Course 1")

    def test_filter_courses_by_field_of_study(self):
        response = self.client.get(reverse('users:courses') + '?field_of_study=1')
        self.assertContains(response, "Course 1")
        self.assertNotContains(response, "Course 2")

    def test_filter_courses_by_level_and_field_of_study(self):
        response = self.client.get(reverse('users:courses') + '?level=beginner&field_of_study=1')
        self.assertContains(response, "Course 1")
        self.assertNotContains(response, "Course 2")


class EnrollmentTests(BaseTestCase):
    """ Test relating the enrollment in the course process. """
    def test_enrolling(self):
        self.client.post(reverse('users:login'), {'username': 'student1', 'password': 'password123'})   
        response = self.client.post(reverse('users:enroll', args=[self.course1.id]))
        self.assertEqual(response.status_code, 200)

        # Parse JSON (and check if user was redirected by JS function)
        response_data = response.json()
        self.assertTrue(response_data.get("success"))

        # Enrollment instance should be created on success
        self.assertTrue(Enrollment.objects.filter(student=self.student_profile, course=self.course1).exists()) 

    def test_unauthenticated_enrolling(self):
        response = self.client.post(reverse('users:enroll', args=[self.course1.id]))
        self.assertEqual(response.status_code, 302) # Expect a redirect to login page


        

        

        

