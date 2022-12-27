# Source: https://stackoverflow.com/questions/33580779/getting-nose-to-ignore-a-function-with-test-in-the-name

from nose.tools import nottest
from studybuddy.models import Course


@nottest
def create_default_test_course():
    test_subject = 'testDept'
    test_catalog_number = 1234
    test_instructor = 'testInstructor'
    test_section = 000
    test_course_number = 12345
    test_description = 'testCourseDescription'

    return Course.objects.create(subject=test_subject,
                                 catalog_number=test_catalog_number,
                                 instructor=test_instructor,
                                 section=test_section,
                                 course_number=test_course_number,
                                 description=test_description)


@nottest
def create_test_course(subject, catalog_number, instructor, section, course_number, description):
    return Course.objects.create(subject=subject,
                                 catalog_number=catalog_number,
                                 instructor=instructor,
                                 section=section,
                                 course_number=course_number,
                                 description=description)
