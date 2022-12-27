# Sources: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing
#          https://stackoverflow.com/questions/58839125/how-to-test-if-a-method-is-called-in-django-rest-framework
from django.urls import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.models import User, Room, Post, Course
from studybuddy.test.test_constants import \
    TEST_USERNAME, \
    TEST_EMAIL, \
    TEST_PASSWORD, \
    TEST_ROOM_NAME, \
    TEST_SUBJECT, \
    TEST_DESCRIPTION, \
    TEST_COURSE_NUMBER, \
    TEST_SECTION, \
    TEST_INSTRUCTOR, \
    TEST_CATALOG_NUMBER, \
    TEST_TOPIC, TEST_PK, TEST_EMAIL2
from studybuddy.views.room_views import room


class RoomsViewTest(TestCase):
    def setUp(self):
        self.test_User = User.objects.create(email=TEST_EMAIL)

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view chat rooms

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/rooms', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        rooms is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:rooms'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        rooms view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:rooms'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studybuddy/rooms.html')

    def test_displays_message_with_no_rooms(self):
        """
        When a user has not been added to any rooms, then there is a message that is shown
        """

        # when
        response = self.client.get(reverse('studybuddy:rooms'))

        # then
        self.assertContains(response, 'You currently do not have any chat rooms.')

    def test_room_is_enterable_when_valid(self):
        """
        When a user is in a chat room, they are able to view it on the chat rooms page
        """
        # given
        test_course = Course.objects.create(subject=TEST_SUBJECT.upper(),
                                            catalog_number=TEST_CATALOG_NUMBER,
                                            instructor=TEST_INSTRUCTOR,
                                            section=TEST_SECTION,
                                            course_number=TEST_COURSE_NUMBER,
                                            description=TEST_DESCRIPTION)

        test_post = Post.objects.create(topic=TEST_TOPIC, course=test_course, user=self.test_User)
        test_room = Room.objects.create(name=TEST_ROOM_NAME, post=test_post)
        test_room.users.add(self.test_User)

        # when
        response = self.client.get(reverse('studybuddy:rooms'))

        # then
        self.assertContains(response, TEST_ROOM_NAME)


class RoomViewTest(TestCase):
    def setUp(self):
        self.test_User = User.objects.create(email=TEST_EMAIL)

        self.test_course = Course.objects.create(subject=TEST_SUBJECT.upper(),
                                            catalog_number=TEST_CATALOG_NUMBER,
                                            instructor=TEST_INSTRUCTOR,
                                            section=TEST_SECTION,
                                            course_number=TEST_COURSE_NUMBER,
                                            description=TEST_DESCRIPTION)

        self.test_post = Post.objects.create(topic=TEST_TOPIC, course=self.test_course, user=self.test_User)
        self.test_room = Room.objects.create(name=TEST_ROOM_NAME, post=self.test_post)
        self.test_room.users.add(self.test_User)

        self.test_request_factory = RequestFactory()

        # mock user login
        self.test_user = get_user_model().objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    def test_view_url_exists_at_desired_location(self):
        """
        url is valid to view a chat room

        Source for "follow=True" - https://stackoverflow.com/questions/21215035/django-test-always-returning-301
        """
        response = self.client.get('/studybuddy/room' + str(TEST_PK), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """
        room view is accessible through its name
        """
        response = self.client.get(reverse('studybuddy:room', args=(TEST_PK,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """
        room view uses the correct template
        """
        response = self.client.get(reverse('studybuddy:room', args=(TEST_PK,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'studybuddy/room.html')

    def test_invalid_room_displays_message(self):
        """
        when a user tries to access an invalid room, a message is displayed
        """
        # given
        Room.objects.all().delete()

        # when
        response = self.client.get(reverse('studybuddy:room', args=(TEST_PK,)))

        # then
        self.assertContains(response, 'The room you are trying to look for does not exist')

    def test_invalid_room_displays_message(self):
        """
        when a user tries to access an invalid room, a message is displayed
        """
        # given
        self.test_room.users.remove(self.test_User)

        # when
        response = self.client.get(reverse('studybuddy:room', args=(TEST_PK,)))

        # then
        self.assertContains(response, 'You are not a user of this room,')

    def test_room_displays(self):
        """
        User sees room name when they enter a room
        """
        # when
        response = self.client.get(reverse('studybuddy:room', args=(TEST_PK,)))

        # then
        self.assertContains(response, self.test_room.__str__())

    def test_room_is_deleted_when_last_user_leaves(self):
        """
        when the last user in the room leaves, the room is deleted
        """
        # given
        test_view_leave_room_request = self.test_request_factory.post(
            '/studybuddy/upcomingSessions', {'leave': 'leave',
                                             'room_pk': TEST_PK})
        test_view_leave_room_request.user = self.test_user
        self.assertEqual(self.test_room.users.all().count(), 1)

        # when
        response = room(test_view_leave_room_request, TEST_PK)

        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.test_room.users.all().count(), 0)
        self.assertEqual(Room.objects.all().count(), 0)

    def test_room_is_not_deleted_when_a_user_leaves(self):
        """
        when a user leaves a room and there are still other users in the room, the room is still viewable
        for the other user(s)
        """
        # given
        test_view_leave_room_request = self.test_request_factory.post(
            '/studybuddy/upcomingSessions', {'leave': 'leave',
                                             'room_pk': TEST_PK})
        test_view_leave_room_request.user = self.test_user
        self.test_room.users.add(User.objects.create(email=TEST_EMAIL2))
        self.assertEqual(self.test_room.users.all().count(), 2)

        # when
        response = room(test_view_leave_room_request, TEST_PK)

        # then
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.test_room.users.all().count(), 1)
        self.assertEqual(Room.objects.all().count(), 1)
