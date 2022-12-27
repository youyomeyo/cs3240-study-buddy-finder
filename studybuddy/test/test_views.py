# Source: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing
import datetime
from unittest import mock
from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.models import User, Course, Post
from studybuddy.test.test_constants import TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD, TEST_SUBJECT, TEST_COURSE_NUMBER, \
    TEST_PK, TEST_DESCRIPTION, TEST_SECTION, TEST_INSTRUCTOR, TEST_CATALOG_NUMBER, TEST_TOPIC
from studybuddy.views import room_views
from studybuddy.views.views import coursefeed


class HomepageViewTest(TestCase):
    def setUp(self):
        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    @mock.patch('studybuddy.models.User.objects')
    def test_after_login_redirect_to_homepage(self, mock_user):
        """
        after user has successfully done google login, they will be redirected to the homepage
        """
        mock_user.filter.exists.return_value = True

        response = self.client.get('/studybuddy/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view the homepage

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        homepage view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:index'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('studybuddy.models.User.objects')
    def test_view_uses_correct_template(self, mock_user):
        """
        homepage view uses the correct template
        """
        # given
        mock_user.filter.return_value = mock_user

        response = self.client.get(reverse('studybuddy:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')


class AllDepartmentViewTest(TestCase):
    def setUp(self):
        User.objects.create(email=TEST_EMAIL)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view all the departments
        """
        response = self.client.get('/studybuddy/alldepartments/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        alldepartments view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:alldepartments'))

        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        alldepartments view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:alldepartments'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'alldepartments.html')


class DepartmentViewTest(TestCase):
    def setUp(self):
        self.test_dept = 'testDept'

        User.objects.create(email=TEST_EMAIL)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view all the departments
        """
        response = self.client.get('/studybuddy/' + self.test_dept, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        department view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:department', args=(self.test_dept,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        department view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:department', args=(self.test_dept,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'department.html')

    def test_no_courses(self):
        """
        If no courses exist, an appropriate message is displayed.
        **this most likely will occur if the department id is incorrect
        """
        response = self.client.get(reverse('studybuddy:department', args=(self.test_dept,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No classes are available in " + self.test_dept.upper() + " or " +
                            self.test_dept.upper() + " does not exist.")

    def test_passing_string_as_dept(self):
        """
        when url received is not a desired format throw a 404 error?
        when url received is not a number still displays desired error message
        """
        pass

    # OH: mocking Department
    # @mock.patch('studybuddy.models.Departments.objects')
    # def test_passing_a_valid_department_courses_are_displayed(self, mock_departments):
    #     """
    #     Add test_dept to Departments Model
    #     Add courses to Course model
    #
    #     Test url that test courses show up
    #     """
    #     # given
    #     test_catalog_number = 1234
    #     test_instructor = 'testInstructor'
    #     test_section = 000
    #     test_course_number = 12345
    #
    #     Departments.objects.create(dept=self.test_dept)
    #
    #     Course.objects.create(subject=self.test_dept,
    #                           catalog_number=test_catalog_number,
    #                           instructor=test_instructor,
    #                           section=test_section,
    #                           course_number=test_course_number)
    #
    #     print(Departments.objects.all())
    #
    #     # when
    #     response = self.client.get(reverse('studybuddy:department', args=(self.test_dept,)))
    #     print(response.content)
    #
    #     # then
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, Course.objects.get(subject=self.test_dept))

    # def test_two_courses(self):
    #     '''
    #     There can be multiple courses to be displayed for a given dept
    #     one of the courses is already added at setup
    #     '''
    #     test_course2 = Course.objects.create(subject=TEST_SUBJECT,
    #                                          catalog_number=self.test_catalog_number,
    #                                          instructor=self.test_instructor,
    #                                          section=self.test_section,
    #                                          course_number=23456,
    #                                          description=self.test_description)
    #


class CourseFeedViewTest(TestCase):
    def setUp(self):
        self.test_catalog_number = 1234
        self.test_instructor = 'testInstructor'
        self.test_section = 000

        self.test_User = User.objects.create(email=TEST_EMAIL)
        self.test_request_factory = RequestFactory()

        test_course = Course.objects.create(subject=TEST_SUBJECT.upper(),
                                            catalog_number=TEST_CATALOG_NUMBER,
                                            instructor=TEST_INSTRUCTOR,
                                            section=TEST_SECTION,
                                            course_number=TEST_COURSE_NUMBER,
                                            description=TEST_DESCRIPTION)

        Post.objects.create(topic=TEST_TOPIC, course=test_course, user=self.test_User)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view the course feed
        """
        response = self.client.get('/studybuddy/' + TEST_SUBJECT + '/' + str(TEST_COURSE_NUMBER), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        coursefeed view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:department', args=(TEST_SUBJECT,)))
        self.assertEqual(response.status_code, 200)

    def test_invalid_course_id(self):
        """
        If a course_number is not in the api, an appropiate message is displayed
        """
        response = self.client.get(
            reverse('studybuddy:coursefeed', args=(TEST_SUBJECT, TEST_COURSE_NUMBER)))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "The department " + TEST_SUBJECT.upper() + " you are looking does not exist "
                                      "or course number " + str(TEST_COURSE_NUMBER) + " in " + TEST_SUBJECT.upper()
                                        + " is not valid.")

    def test_view_uses_correct_template(self):
        """
        coursefeed view uses the correct template
        """
        response = self.client.get(
            reverse('studybuddy:coursefeed', args=(TEST_SUBJECT, TEST_COURSE_NUMBER)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'course_feed.html')

    def test_view_nofeed(self):
        """
        when there are no study buddy posts for the course, the feed displays appropriate message
        """
        response = self.client.get(
            reverse('studybuddy:coursefeed', args=(TEST_SUBJECT, TEST_COURSE_NUMBER)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are currently no posts made for this class")

    @mock.patch('studybuddy.views.post_views.deletepost')
    def test_delete_calls_method(self, mock_deletepost):
        """
        when a user declines a study session, the decline method is called
        """
        # given
        test_view_delete_post_request = self.test_request_factory.post(
            '/studybuddy/coursefeed/' + TEST_SUBJECT + str(TEST_COURSE_NUMBER), {'delete': 'delete',
                                                                                 'post_pk': TEST_PK})
        test_view_delete_post_request.user = self.test_user

        # when
        response = coursefeed(test_view_delete_post_request, TEST_SUBJECT, TEST_COURSE_NUMBER)

        # then
        self.assertEqual(response.status_code, 200)
        mock_deletepost.assert_called_once_with(test_view_delete_post_request)

    @mock.patch('studybuddy.views.room_views.addRoom')
    def test_delete_calls_add_roommethod(self, mock_addRoom):
        """
        when a user declines a study session, the decline method is called
        """
        # given
        test_view_message_post_request = self.test_request_factory.post(
            '/studybuddy/coursefeed/' + TEST_SUBJECT + str(TEST_COURSE_NUMBER), {'message': 'message',
                                                                                 'post_pk': TEST_PK})
        test_view_message_post_request.user = self.test_user
        mock_addRoom.return_value = 1

        # when
        response = coursefeed(test_view_message_post_request, TEST_SUBJECT, TEST_COURSE_NUMBER)

        # then
        self.assertEqual(response.status_code, 200)
        mock_addRoom.assert_called_once_with(test_view_message_post_request)

    @mock.patch('studybuddy.views.room_views.room')
    def test_delete_calls_room_method(self, mock_room):
        """
        when a user declines a study session, the decline method is called
        """
        # given
        test_view_message_post_request = self.test_request_factory.post(
            '/studybuddy/coursefeed/' + TEST_SUBJECT + str(TEST_COURSE_NUMBER), {'message': 'message',
                                                                                 'post_pk': TEST_PK})
        test_view_message_post_request.user = self.test_user

        # when
        coursefeed(test_view_message_post_request, TEST_SUBJECT, TEST_COURSE_NUMBER)

        # then
        mock_room.assert_called_once_with(test_view_message_post_request, room_views.addRoom(test_view_message_post_request))

    # Source: https://stackoverflow.com/questions/45512749/how-to-mock-a-django-model-object-along-with-its-methods

    # OH: mocking course and feed
    # @mock.patch('studybuddy.models.Course.objects', 'studybuddy.models.Post.objects')
    # def test_views_displays_feed(self, mock_course, mock_post):
    #     """
    #     when there are study buddy post for the course, the feed displays
    #     """
    #
    #     # given
    #     test_topic = "test_topic"
    #     test_description = "test_description"
    #
    #     Departments.objects.create(dept=TEST_SUBJECT.upper())
    #
    #     # test_course = Course.objects.create(subject=TEST_SUBJECT.upper(),
    #     #                       catalog_number=self.test_catalog_number,
    #     #                       instructor=self.test_instructor,
    #     #                       section=self.test_section,
    #     #                       course_number=self.test_course_number)
    #
    #     test_user = User.objects.create(email=self.test_email)
    #
    #     # test_post = Post.objects.create(course=test_course,
    #     #                     user=test_user,
    #     #                     author=TEST_USERNAME,
    #     #                     topic=test_topic,
    #     #                     startDate=timezone.now(),
    #     #                     endDate=timezone.now() + datetime.timedelta(days=7),
    #     #                     description=test_description)
    #
    #     mock_course.filter.exists.return_value = True
    #     mock_course.filter.return_value = mock_course #test_course
    #     mock_post.filter.return_value = mock_post #test_post
    #
    #     # when
    #     response = self.client.get(
    #         reverse('studybuddy:coursefeed', args=(TEST_SUBJECT, self.test_course_number)))
    #
    #     # then
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, test_topic)


class EnrollViewTest(TestCase):
    def setUp(self):
        self.test_dept = 'testDept'
        self.test_email = 'test2@email.com'
        self.test_catalog_number = 1234
        self.test_instructor = 'testInstructor'
        self.test_section = 000
        self.test_course_number = 12345

        Course.objects.create(subject=self.test_dept,
                              catalog_number=self.test_catalog_number,
                              instructor=self.test_instructor,
                              section=self.test_section,
                              course_number=self.test_course_number)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, self.test_email, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    @mock.patch('studybuddy.models.User.objects')
    def test_view_uses_correct_template(self, mock_user):
        """
        enroll view uses the correct template
        """
        # given
        mock_user.get.return_value = mock_user

        # when
        response = self.client.get(reverse('studybuddy:enroll', args=(self.test_dept, self.test_course_number)))

        # then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'enroll.html')
