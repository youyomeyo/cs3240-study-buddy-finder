# Sources: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing
#          https://stackoverflow.com/questions/58839125/how-to-test-if-a-method-is-called-in-django-rest-framework
from unittest import mock
from django.urls import reverse
from django.test import TestCase
from studybuddy.models import Course, User
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.views.post_views import viewposts
from studybuddy.test.test_constants import TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD, TEST_SUBJECT


class MakePostViewTest(TestCase):
    def setUp(self):
        self.test_catalog_number = 1234
        self.test_instructor = 'testInstructor'
        self.test_section = 000
        self.test_course_number = 12345
        self.test_description = 'testCourseDescription'

        User.objects.create(email=TEST_EMAIL)

        Course.objects.create(subject=TEST_SUBJECT.upper(),
                              catalog_number=self.test_catalog_number,
                              instructor=self.test_instructor,
                              section=self.test_section,
                              course_number=self.test_course_number,
                              description=self.test_description)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to make a post

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/' + TEST_SUBJECT + '/' + str(self.test_course_number) + '/makepost',
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        makepost view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:makepost', args=(TEST_SUBJECT,
                                                                        self.test_course_number)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        makepost view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:makepost', args=(TEST_SUBJECT,
                                                                        self.test_course_number)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post/makepost.html')

    def test_invalid_dept_shows_message(self):
        """
        when given an invalid course number/department, the template renders the correct information
        """
        # given
        expected_response = 'The course number ' + str(self.test_course_number) + ' in ' + TEST_SUBJECT.upper() + \
                            ' is not available to make a post'

        Course.objects.all().delete()

        # when
        response = self.client.get(reverse('studybuddy:makepost', args=(TEST_SUBJECT,
                                                                        self.test_course_number)))

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_response)

    def test_valid_course_shows_make_post_form(self):
        """
        when given a valid course number/department, the template render the form to make a post
        """
        # when
        response = self.client.get(reverse('studybuddy:makepost', args=(TEST_SUBJECT,
                                                                        self.test_course_number)))

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Make a study buddy post for: ')
        self.assertContains(response, TEST_SUBJECT.upper() + str(self.test_catalog_number))


class ViewPostViewTest(TestCase):
    def setUp(self):
        self.test_request_factory = RequestFactory()

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid for user to view their posts

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        # given
        User.objects.create(email=TEST_EMAIL)

        # when
        response = self.client.get('/studybuddy/viewposts', follow=True)

        # then
        self.assertEqual(response.status_code, 200)

    @mock.patch('studybuddy.models.User.objects')
    def test_view_url_accessible_by_name(self, mock_user):
        """
        viewposts view is accessible through its name
        """
        # given
        mock_user.get.return_value = mock_user

        # when
        response = self.client.get(reverse('studybuddy:viewposts'))

        # then
        self.assertEqual(response.status_code, 200)

    @mock.patch('studybuddy.models.User.objects')
    def test_view_uses_correct_template(self, mock_user):
        """
        viewposts view uses the correct template
        """
        # given
        mock_user.get.return_value = mock_user

        # when
        response = self.client.get(reverse('studybuddy:viewposts'))

        # then
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post/viewposts.html')

    @mock.patch('studybuddy.views.post_views.deletepost')
    def test_delete_request_calls_delete(self, mock_deletepost):
        """
        when user deletes a post, the delete method is called
        """
        # given
        User.objects.create(email=TEST_EMAIL)

        test_view_delete_request = self.test_request_factory.post(
            '/studybuddy/viewposts', {'delete' : 'Delete Post', })
        test_view_delete_request.user = self.test_user

        # when
        response = viewposts(test_view_delete_request)

        # then
        self.assertEqual(response.status_code, 200)
        mock_deletepost.assert_called_once_with(test_view_delete_request)
