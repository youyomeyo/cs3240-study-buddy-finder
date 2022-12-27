from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.models import User, Friend_Request
from studybuddy.test.test_constants import TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD, TEST_FRIEND_EMAIL
from studybuddy.views.friend_views import accept_friend_request, decline_request, remove_friend, send_friend_request


class FriendActionTests(TestCase):
    def setUp(self):
        self.test_username2 = 'testFriendName'
        self.test_password2 = 'testFriendPassword'

        self.test_request_factory = RequestFactory()
        self.test_user1 = User.objects.create(email=TEST_EMAIL)
        self.test_user2 = User.objects.create(email=TEST_FRIEND_EMAIL)

        Friend_Request.objects.create(to_user=self.test_user2, from_user=self.test_user1)

        self.test_user1 = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.test_user2 = get_user_model().objects.create_user(self.test_username2,
                                                               TEST_FRIEND_EMAIL,
                                                               self.test_password2)

        # mock requests
        self.test_view_accept_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'accept': 'accept',
                                    'ad_email': TEST_EMAIL})
        self.test_view_accept_friend_request.user = self.test_user2

        self.test_view_send_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'request': 'request',
                                    'toEmail': TEST_FRIEND_EMAIL})
        self.test_view_send_friend_request.user = self.test_user1

    def test_sent_friend_request_creates_request(self):
        """
        when a user sends a friend request, the friend request is sent to the desired user
        """
        # given
        Friend_Request.objects.all().delete()

        # when
        response = send_friend_request(self.test_view_send_friend_request, TEST_FRIEND_EMAIL)

        # then
        self.assertEqual(Friend_Request.objects.filter(to_user=TEST_FRIEND_EMAIL).count(), 1)
        self.assertEqual(response, 1)

    def test_resending_friend_request(self):
        """
        when a user resends a friend request, send friend method returns 0
        """
        # when
        response = send_friend_request(self.test_view_send_friend_request, TEST_FRIEND_EMAIL)

        # then
        self.assertEqual(Friend_Request.objects.filter(to_user=TEST_FRIEND_EMAIL).count(), 1)
        self.assertEqual(response, 0)

    def test_friend_request_to_existing_friend(self):
        """
        when a user sends a friend request to a user they are already friend with, send friend method returns 2
        """
        # given
        accept_friend_request(self.test_view_accept_friend_request, TEST_EMAIL)

        # when
        response = send_friend_request(self.test_view_send_friend_request, TEST_FRIEND_EMAIL)

        # then
        self.assertEqual(response, 2)

    def test_accept_adds_friend(self):
        """
        when a user accepts a friend request, the user is added to each other's friend list
        """
        # given
        self.assertEqual(User.objects.get(email=TEST_EMAIL).friends.count(), 0)

        # when
        accept_friend_request(self.test_view_accept_friend_request, TEST_EMAIL)

        # then
        self.assertEqual(User.objects.get(email=TEST_EMAIL).friends.count(), 1)
        self.assertEqual(User.objects.get(email=TEST_FRIEND_EMAIL).friends.count(), 1)

    def test_no_valid_friend_request(self):
        """
        when a friend request doesn't exist, accept returns 0
        """
        # given
        test_view_no_valid_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'accept': 'accept',
                                    'ad_email': TEST_EMAIL})
        test_view_no_valid_friend_request.user = self.test_user1

        # when
        response = accept_friend_request(test_view_no_valid_friend_request, TEST_FRIEND_EMAIL)

        # then
        self.assertEqual(response, 0)

    def test_decline_removes_friend_request(self):
        """
        when a user declines a friend request, the friend request is removed
        """
        # given
        test_view_decline_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'decline': 'decline',
                                    'ad_email': TEST_EMAIL})
        test_view_decline_friend_request.user = self.test_user2

        self.assertEqual(Friend_Request.objects.filter(to_user=TEST_FRIEND_EMAIL).count(), 1)

        # when
        decline_request(test_view_decline_friend_request, TEST_EMAIL)

        # then
        self.assertEqual(Friend_Request.objects.filter(to_user=TEST_FRIEND_EMAIL).count(), 0)

    def test_unfriend_request_removes_friend(self):
        """
        when a user removes a friend request, the friend request is deleted
        """
        # given
        test_view_remove_friend_request = self.test_request_factory.post(
            '/studybuddy/friends', {'unfriend': 'unfriend',
                                    'remove_email': TEST_FRIEND_EMAIL})
        test_view_remove_friend_request.user = self.test_user1
        accept_friend_request(self.test_view_accept_friend_request, TEST_EMAIL)

        self.assertEqual(User.objects.get(email=TEST_EMAIL).friends.count(), 1)
        self.assertEqual(User.objects.get(email=TEST_FRIEND_EMAIL).friends.count(), 1)

        # when
        remove_friend(test_view_remove_friend_request, TEST_FRIEND_EMAIL)

        # then
        self.assertEqual(User.objects.get(email=TEST_EMAIL).friends.count(), 0)
        self.assertEqual(User.objects.get(email=TEST_FRIEND_EMAIL).friends.count(), 0)


