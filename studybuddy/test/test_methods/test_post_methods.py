# Sources: https://stackoverflow.com/questions/2036202/how-to-mock-users-and-requests-in-django
#          https://docs.djangoproject.com/en/4.1/topics/testing/advanced/

from django.test import TestCase
from studybuddy.models import User, Course, Post
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from studybuddy.views.post_views import submitpost, deletepost


class SubmitPostTest(TestCase):
    def setUp(self):
        self.test_email = 'test@email.com'
        self.test_username = 'testName'
        self.test_password = 'testPassword'
        self.test_dept = 'testDept'
        self.test_catalog_number = 1234
        self.test_instructor = 'testInstructor'
        self.test_section = 000
        self.test_course_number = 12345
        self.test_description = 'testCourseDescription'

        self.test_request_factory = RequestFactory()
        self.test_user = get_user_model().objects.create_user(self.test_username, self.test_email, self.test_password)

        User.objects.create(email=self.test_email)

        self.test_course = Course.objects.create(subject=self.test_dept.upper(),
                                                 catalog_number=self.test_catalog_number,
                                                 instructor=self.test_instructor,
                                                 section=self.test_section,
                                                 course_number=self.test_course_number,
                                                 description=self.test_description)

    def test_submit_post_default_values(self):
        """
        test submitpost makes a post with default values when given user doesn't fill in any information
        """
        # given
        test_post_request = self.test_request_factory.post(
            '/studybuddy/' + self.test_dept + str(self.test_course_number),
            {'start_date': '',
             'end_date': '',
             'topic': '',
             'description': '',
             'post_type': 'section'})
        test_post_request.user = self.test_user

        # when
        test_submit = submitpost(test_post_request, self.test_dept, self.test_course_number)

        # then
        self.assertEquals(Post.objects.filter(course=self.test_course).count(), 1)
        self.assertEqual(test_submit, 1)

        test_new_default_post = Post.objects.get(course=self.test_course)
        self.assertEquals(test_new_default_post.topic, "No topic was provided by the author of this post")
        self.assertEquals(test_new_default_post.description, "No description was provided by the author of this post")

    def test_submit_post_with_values(self):
        """
        test submitpost makes a post with values provided by the user
        """
        # given
        test_post_request = self.test_request_factory.post(
            '/studybuddy/' + self.test_dept + str(self.test_course_number),
            {'start_date': '2023-01-01',
             'end_date': '2023-01-02',
             'topic': 'test_topic',
             'description': 'test_desciption',
             'post_type': 'section'})
        test_post_request.user = self.test_user

        # when
        test_submit = submitpost(test_post_request, self.test_dept, self.test_course_number)

        # then
        self.assertEquals(Post.objects.filter(course=self.test_course).count(), 1)
        self.assertEqual(test_submit, 1)

        test_new_post = Post.objects.get(course=self.test_course)
        self.assertEquals(test_new_post.topic, "test_topic")
        self.assertEquals(test_new_post.description, "test_desciption")

    def test_submit_post_for_whole_course(self):
        """
        test submitpost makes a post and associates with all courses with same catalog and department
        """
        # given
        test_post_request = self.test_request_factory.post(
            '/studybuddy/' + self.test_dept + str(self.test_course_number),
            {'start_date': '',
             'end_date': '',
             'topic': '',
             'description': '',
             'post_type': 'course'})
        test_post_request.user = self.test_user

        Course.objects.create(subject=self.test_dept.upper(),
                              catalog_number=self.test_catalog_number,
                              instructor=self.test_instructor,
                              section=self.test_section,
                              course_number=23456,
                              description=self.test_description)

        # when
        test_submit = submitpost(test_post_request, self.test_dept, self.test_course_number)

        # then
        self.assertEqual(Post.objects.filter(course=self.test_course).count(), 1)
        self.assertEqual(test_submit, 1)

        test_new_post = Post.objects.get(course=self.test_course)
        self.assertEquals(test_new_post.post_type, "course")

    def test_submit_post_returns_0(self):
        """
        test submit post returns 0 when the course is not found
        """
        test_post_request = self.test_request_factory.post(
            '/studybuddy/' + self.test_dept + str(23456),
            {'start_date': '',
             'end_date': '',
             'topic': '',
             'description': '',
             'post_type': 'course'})
        test_post_request.user = self.test_user

        # when
        test_submit = submitpost(test_post_request, self.test_dept, 23456)

        # then
        self.assertEqual(test_submit, 0)


class DeletePostTest(TestCase):
    def setUp(self):
        self.test_email = 'test@email.com'
        self.test_username = 'testName'
        self.test_password = 'testPassword'
        self.test_dept = 'testDept'
        self.test_catalog_number = 1234
        self.test_instructor = 'testInstructor'
        self.test_section = 000
        self.test_course_number = 12345
        self.test_description = 'testCourseDescription'

        self.test_request_factory = RequestFactory()
        self.test_user = get_user_model().objects.create_user(self.test_username, self.test_email, self.test_password)

        User.objects.create(email=self.test_email)

        self.test_course = Course.objects.create(subject=self.test_dept.upper(),
                                                 catalog_number=self.test_catalog_number,
                                                 instructor=self.test_instructor,
                                                 section=self.test_section,
                                                 course_number=self.test_course_number,
                                                 description=self.test_description)

    def test_delete_post_removes_correct_post(self):
        """
        delete posts removes the post
        """
        # given
        test_post_request = self.test_request_factory.post(
            '/studybuddy/' + self.test_dept + str(23456),
            {'start_date': '',
             'end_date': '',
             'topic': '',
             'description': '',
             'post_type': 'course'})
        test_post_request.user = self.test_user
        submitpost(test_post_request, self.test_dept, self.test_course_number)

        test_delete_request = self.test_request_factory.post(
            '/studybuddy/' + self.test_dept + str(self.test_course_number), {'post_pk': 1, })
        test_delete_request.user = self.test_user

        self.assertEqual(Post.objects.filter(course=self.test_course).count(), 1)

        # when
        deletepost(test_delete_request)

        # then
        self.assertEquals(Post.objects.filter(course=self.test_course).count(), 0)
