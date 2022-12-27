from django.test import TestCase
from studybuddy.models import User, Course, Post, StudySession, EnrolledClass
from studybuddy.test.test_constants import \
    TEST_SUBJECT, \
    TEST_CATALOG_NUMBER, \
    TEST_INSTRUCTOR, \
    TEST_SECTION, \
    TEST_COURSE_NUMBER, \
    TEST_DESCRIPTION


class CourseTest(TestCase):
    def setUp(self):
        self.test_course = Course.objects.create(subject=TEST_SUBJECT,
                                                 catalog_number=TEST_CATALOG_NUMBER,
                                                 instructor=TEST_INSTRUCTOR,
                                                 section=TEST_SECTION,
                                                 course_number=TEST_COURSE_NUMBER,
                                                 description=TEST_DESCRIPTION)

    def test_course_str(self):
        """
        Check the _str_ methods displays correctly when a course has all valid value
        """
        # given
        expectedStr = TEST_SUBJECT + str(TEST_CATALOG_NUMBER) + ": " + TEST_DESCRIPTION + ' \n ' + \
                      'Instructor: ' + TEST_INSTRUCTOR + ' \n ' + \
                      '(Section: ' + str(TEST_SECTION) + ')'

        # then
        self.assertEqual(self.test_course.__str__(), expectedStr)

    def test_no_instructor_available(self):
        """
        Check the _str_ methods displays correctly with instructor is '-'
        """
        # given
        test_course = Course(subject=TEST_SUBJECT,
                             catalog_number=TEST_CATALOG_NUMBER,
                             instructor='-',
                             section=TEST_SECTION,
                             course_number=TEST_COURSE_NUMBER,
                             description=TEST_DESCRIPTION)

        # then
        expectedStr = TEST_SUBJECT + str(TEST_CATALOG_NUMBER) + ": " + TEST_DESCRIPTION + ' \n ' + \
                      'Instructor: Not available' + ' \n ' + \
                      '(Section: ' + str(TEST_SECTION) + ')'
        self.assertEqual(test_course.__str__(), expectedStr)

    def test_subject_label(self):
        expected_label = self.test_course._meta.get_field('subject').verbose_name
        self.assertEqual(expected_label, 'subject')


class UserTest(TestCase):
    def test_default(self):
        account = User(email="abc@gmail.com")
        self.assertEqual(account.email, "abc@gmail.com")
        self.assertEqual(account.name, "")
        self.assertEqual(account.zoomLink, "")
        self.assertEqual(account.blurb, "")

    def test_update(self):
        account = User(email="abc2@gmail.com")
        account.name = "abc"
        account.blurb = "hi my name is abc"
        self.assertEqual(account.email, "abc2@gmail.com")
        self.assertEqual(account.name, "abc")
        self.assertEqual(account.zoomLink, "")
        self.assertEqual(account.blurb, "hi my name is abc")


class EnrollTest(TestCase):
    def add_class(self):
        account = User(email="abc3@gmail.com", firstName="abc", lastName="def")
        test_course = Course.objects.get(id=1)
        enroll = EnrolledClass(course=test_course, student=account)
        enrolled_course = account.enrolledclass_set.all()
        num_enrolled_course = account.enrolledclass_set.count()
        self.assertTrue(EnrolledClass.objects.filter(course=test_course, student=account).exists())
        self.assertEqual(num_enrolled_course, 1)


class PostTest(TestCase):
    def setUp(self):
        self.test_course = Course.objects.create(subject=TEST_SUBJECT,
                                                 catalog_number=TEST_CATALOG_NUMBER,
                                                 instructor=TEST_INSTRUCTOR,
                                                 section=TEST_SECTION,
                                                 course_number=TEST_COURSE_NUMBER,
                                                 description=TEST_DESCRIPTION)

        self.test_email = 'test@email.com'

        self.test_user = User.objects.create(email=self.test_email)

        self.test_author = 'testAuthor'
        self.test_topic = 'test_topic'
        self.start_date = '2023-01-01'
        self.end_date = '2023-01-02'

        Post.objects.create(course=self.test_course,
                            user=self.test_user,
                            author=self.test_author,
                            topic=self.test_topic,
                            startDate=self.start_date,
                            endDate=self.end_date)

    def test_post_str(self):
        """
        Check _str_ methods returns correctly for Posts
        """
        # given
        expectedStr = self.test_topic + '\n' + \
                      'Author: ' + self.test_author + '\n' + \
                      '01-01-2023' + ' to ' + '01-02-2023' + '\n'

        # when
        actualStr = Post.objects.get(author=self.test_author).__str__()

        # then
        self.assertEqual(actualStr, expectedStr)

    def test_post_cascades_when_users_is_deleted(self):
        """
        when a user is deleted, the posts they have made are also deleted
        """
        # given
        self.assertEqual(Post.objects.filter(user=self.test_user).count(), 1)
        User.objects.filter(email=self.test_email).delete()

        # then
        self.assertEqual(Post.objects.filter(user=self.test_user).count(), 0)

    def test_post_cascades_when_course_is_deleted(self):
        """
        when a course is removed from the system, the posts related to the course is also deleted
        """
        # given
        self.assertEqual(Post.objects.filter(course=self.test_course).count(), 1)
        Course.objects.filter(course_number=TEST_COURSE_NUMBER).delete()

        # then
        self.assertEqual(Post.objects.filter(course=self.test_course).count(), 0)


class StudySessionTest(TestCase):
    def setUp(self):
        self.test_name = 'testName'
        self.test_date = '2023-01-01'
        self.test_start = '11:22'
        self.test_end = '12:22'
        self.test_accepted = '?'

        StudySession.objects.create(name=self.test_name,
                                    date=self.test_date,
                                    start=self.test_start,
                                    end=self.test_end)

    def test_study_session_str(self):
        """
        check __str__ methods return correctly for StudySession
        """
        # given
        expected_str = "Study session for: " + self.test_name + '\n' \
                       + "Scheduled on: " + '01-01-2023' + '\n' \
                       + 'Time Frame: ' + self.test_start + ' to ' + self.test_end

        # when
        actual_str = StudySession.objects.get(name=self.test_name).__str__()

        # then
        self.assertEqual(actual_str, expected_str)
