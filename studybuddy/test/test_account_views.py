from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.models import User
from studybuddy.views.views import addAccount
from studybuddy.test.test_constants import TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD


# class IndexViewTest(TestCase):
#     def setUp(self):
#         self.test_request_factory = RequestFactory()
#
#     @mock.patch('studybuddy.views.views.addAccount')
#     def test_new_user_method_is_called(self, mock_addAccount):
#         # given
#         test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
#         test_add_account_request = self.test_request_factory.post('', {})
#         test_add_account_request.user = test_user
#         self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
#
#         # when
#         index(test_add_account_request)
#
#         # then
#         mock_addAccount.assert_called_once_with(test_add_account_request)


class AddAccountViewTest(TestCase):
    def setUp(self):
        self.test_request_factory = RequestFactory()

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_add_account_adds_to_user_model(self):
        """
        when a new user joins, their account is added
        """
        # given
        test_add_account_request = self.test_request_factory.post('', {})
        test_add_account_request.user = self.test_user

        # when
        addAccount(test_add_account_request)

        # then
        self.assertEqual(User.objects.all().count(), 1)


class AccountViewTest(TestCase):
    def setUp(self):
        User.objects.create(email=TEST_EMAIL)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view account

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/account', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        account view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:account'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        account view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studybuddy/account.html')


class EditAccountViewTest(TestCase):
    def setUp(self):
        User.objects.create(email=TEST_EMAIL)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to edit account

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/account/edit', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        edit account view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:editAccount'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        edit account view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:editAccount'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studybuddy/editAccount.html')
