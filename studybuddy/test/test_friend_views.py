from unittest import mock
from django.urls import reverse
from django.test import TestCase
from studybuddy.models import User, Friend_Request
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.views.friend_views import view_friends, accept_friend_request
from studybuddy.test.test_constants import TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD, TEST_FRIEND_EMAIL


class FriendViewTest(TestCase):
    def setUp(self):
        User.objects.create(email=TEST_EMAIL)
        self.test_request_factory = RequestFactory()

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        # mock requests
        self.test_view_accept_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'accept': 'accept',
                                    'ad_email': TEST_FRIEND_EMAIL})
        self.test_view_accept_friend_request.user = self.test_user

        self.test_view_send_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'request': 'request',
                                    'email': TEST_FRIEND_EMAIL})
        self.test_view_send_friend_request.user = self.test_user

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view friends and friend requests

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/friends', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        view friends view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:viewFriends'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        view friends view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:viewFriends'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friends/view_friends.html')

    @mock.patch('studybuddy.views.friend_views.accept_friend_request')
    def test_accept_calls_method(self, mock_accept_friend_request):
        """
        when a user accepts a friend request, the accept method is called
        """
        # when
        response = view_friends(self.test_view_accept_friend_request)

        # then
        self.assertEqual(response.status_code, 200)
        mock_accept_friend_request.assert_called_once_with(self.test_view_accept_friend_request, TEST_FRIEND_EMAIL)

    @mock.patch('studybuddy.views.friend_views.decline_request')
    def test_decline_calls_method(self, mock_decline_request):
        """
        when a user decline a friend request, the decline method is called
        """
        # given
        test_view_decline_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'decline': 'decline',
                                    'ad_email': TEST_FRIEND_EMAIL})
        test_view_decline_friend_request.user = self.test_user

        # when
        response = view_friends(test_view_decline_friend_request)

        # then
        self.assertEqual(response.status_code, 200)
        mock_decline_request.assert_called_once_with(test_view_decline_friend_request, TEST_FRIEND_EMAIL)

    @mock.patch('studybuddy.views.friend_views.remove_friend')
    def test_remove_calls_method(self, mock_remove_friend):
        """
        when a user removes a friend, the remove method is called
        """
        # given
        test_view_remove_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'unfriend': 'unfriend',
                                    'remove_email': TEST_FRIEND_EMAIL})
        test_view_remove_friend_request.user = self.test_user

        # when
        response = view_friends(test_view_remove_friend_request)

        # then
        self.assertEqual(response.status_code, 200)
        mock_remove_friend.assert_called_once_with(test_view_remove_friend_request, TEST_FRIEND_EMAIL)

    @mock.patch('studybuddy.views.friend_views.view_friend_profile')
    def test_view_friend_method(self, mock_view_friend_profile):
        """
        when a user views a friend's profile, the view friend profile method is called
        """
        # given
        test_view_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'view_friends': 'view_friends',
                                    'friend_email': TEST_FRIEND_EMAIL})
        test_view_friend_request.user = self.test_user

        # when
        view_friends(test_view_friend_request)

        # then
        mock_view_friend_profile.assert_called_once_with(test_view_friend_request, TEST_FRIEND_EMAIL)

    def test_view_friend_profile_renders_template(self):
        """
        view friend profile renders correct information
        """
        # given
        test_view_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'view_friends': 'view_friends',
                                    'friend_email': TEST_FRIEND_EMAIL})
        test_view_friend_request.user = self.test_user

        User.objects.create(email=TEST_FRIEND_EMAIL)

        # when
        response = view_friends(test_view_friend_request)

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testFriend@email.com')

    def test_send_friend_request_displays_message(self):
        """
        when a user has successfully sent a friend request, they receive a message
        """
        # given
        User.objects.create(email=TEST_FRIEND_EMAIL)

        # when
        response = view_friends(self.test_view_send_friend_request)

        print(response.content)

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have successfully sent a friend request to ' + TEST_FRIEND_EMAIL +
                            '. Their email will show up on your')

    def test_send_friend_request_to_self_displays_message(self):
        """
        when a user tries to send a friend request to themself, they receive a message
        """
        # given
        User.objects.create(email=TEST_FRIEND_EMAIL)

        test_view_send_friend_request_self = self.test_request_factory.post(
            '/studybuddy/friends', {'request': 'request',
                                    'email': TEST_EMAIL})
        test_view_send_friend_request_self.user = self.test_user

        # when
        response = view_friends(test_view_send_friend_request_self)

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The email ' + TEST_EMAIL + ' you entered belongs to you')

    def test_send_friend_request_to_existing_friend(self):
        """
        when a user tries to send a friend request to a user they already friends with, they receive a message
        """
        # given
        User.objects.create(email=TEST_FRIEND_EMAIL)
        User.objects.get(email=TEST_EMAIL).friends.add(User.objects.get(email=TEST_FRIEND_EMAIL))
        User.objects.get(email=TEST_FRIEND_EMAIL).friends.add(User.objects.get(email=TEST_EMAIL))

        # when
        response = view_friends(self.test_view_send_friend_request)

        print(response.content)

        # then
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are already friends with user with email ' + TEST_FRIEND_EMAIL + '. You can '
                                      'see them in the')

    # def test_resend_friend_displays_message(self):
    #     """
    #     when a user tries to resend a friend request, they receive a message
    #     """
    #     # given
    #     User.objects.create(email=TEST_FRIEND_EMAIL)
    #     Friend_Request.objects.create(to_user=User.objects.get(email=TEST_FRIEND_EMAIL),
    #                                   from_user=User.objects.get(email=TEST_EMAIL))
    #     accept_friend_request(self.test_view_accept_friend_request, TEST_FRIEND_EMAIL)
    #
    #     # when
    #     response = view_friends(self.test_view_send_friend_request)
    #
    #     print(response.content)
    #
    #     # then
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'You have already sent a friend request to ' + TEST_EMAIL + ', its pending '
    #                                    'acceptance from the user')
