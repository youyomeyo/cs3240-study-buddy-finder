# Sources: https://stackoverflow.com/questions/2036202/how-to-mock-users-and-requests-in-django
#          https://docs.djangoproject.com/en/4.1/topics/testing/advanced/

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.models import User, StudySession
from studybuddy.views.study_session_views import acceptSession, declineSession, deleteSession


class StudySessionActionsTest(TestCase):
    def setUp(self):
        self.test_email = 'test@email.com'
        self.test_username = 'testName'
        self.test_password = 'testPassword'
        self.test_study_session_name = 'testStudySession'
        self.test_date = '2023-01-01'
        self.test_start_time = '01:30'
        self.test_end_time = '2:30'
        self.test_accepted_status = '?'

        self.test_request_factory = RequestFactory()
        User.objects.create(email=self.test_email)

        self.test_user = get_user_model().objects.create_user(self.test_username, self.test_email, self.test_password)

        self.test_study_session = StudySession.objects.create(name=self.test_study_session_name,
                                    date=self.test_date,
                                    start=self.test_start_time,
                                    end=self.test_end_time,
                                    accepted=self.test_accepted_status)

    def test_accept_study_session_changes_accepted_status(self):
        """
        when a user accepts a study session, the accepted status is set to yes
        """
        # given
        test_view_accept_session_request = self.test_request_factory.post(
            '/studybuddy/upcomingSessions', {'accept': 'accept',
                                             'session_pk': 1})
        test_view_accept_session_request.user = self.test_user

        # when
        acceptSession(test_view_accept_session_request)

        # then
        self.assertEqual(StudySession.objects.get(pk=1).accepted, 'yes')

    def test_decline_study_session_updates_session(self):
        """
        when a user declines a study session, the accepted and date is updated
        """
        # given
        test_view_decline_session_request = self.test_request_factory.post(
            '/studybuddy/upcomingSessions', {'decline': 'decline',
                                             'session_pk': 1})
        test_view_decline_session_request.user = self.test_user

        # when
        declineSession(test_view_decline_session_request)

        # then
        self.assertEqual(StudySession.objects.get(pk=1).accepted, 'no')
        self.assertNotEqual(StudySession.objects.get(pk=1).date, self.test_date)

    def test_delete_study_session_removes_session(self):
        """
        when a user deletes a study session, the study session is removed
        """
        # given
        test_view_delete_session_request = self.test_request_factory.post(
            '/studybuddy/upcomingSessions', {'delete': 'delete',
                                             'session_pk': 1})
        test_view_delete_session_request.user = self.test_user
        self.assertEqual(StudySession.objects.count(), 1)

        # when
        deleteSession(test_view_delete_session_request)

        # then
        self.assertEqual(StudySession.objects.count(), 0)
        self.assertEqual(StudySession.objects.filter(name = self.test_study_session_name).exists(), False)
