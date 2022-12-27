from django.urls import reverse
from django.test import TestCase
from studybuddy.test.test_constants import TEST_DEPT, TEST_COURSE_NUMBER, TEST_PK


class LoginViewTest(TestCase):
    """
    When the user is not logged in, all of the pages except index and all departments,
    because they are classes will use the index.html template
    """

    def test_homepage(self):
        response = self.client.get(reverse('studybuddy:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_friends(self):
        response = self.client.get(reverse('studybuddy:viewFriends'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_account(self):
        response = self.client.get(reverse('studybuddy:account'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_addAccount(self):
        response = self.client.get(reverse('studybuddy:addAccount'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_editAccount(self):
        response = self.client.get(reverse('studybuddy:editAccount'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_updateAccount(self):
        response = self.client.get(reverse('studybuddy:updateAccount'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_alldepartments(self):
        response = self.client.get(reverse('studybuddy:alldepartments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_department(self):
        response = self.client.get(reverse('studybuddy:department', args=(TEST_DEPT,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_coursefeed(self):
        response = self.client.get(reverse('studybuddy:coursefeed', args=(TEST_DEPT,
                                                                          TEST_COURSE_NUMBER)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_makepost(self):
        response = self.client.get(reverse('studybuddy:makepost', args=(TEST_DEPT,
                                                                        TEST_COURSE_NUMBER)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_viewposts(self):
        response = self.client.get(reverse('studybuddy:viewposts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_schedule(self):
        response = self.client.get(reverse('studybuddy:schedule', args=(TEST_PK,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    # def test_enroll(self):
    #     response = self.client.get(reverse('studybuddy:enroll', args=(TEST_COURSE_NUMBER,)))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Do you want to study with me?")
    #     self.assertTemplateUsed(response, 'index.html')
    #
    # def test_update_course_load(self):
    #     response = self.client.get(reverse('studybuddy:ucl', args=(TEST_COURSE_NUMBER,)))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "Do you want to study with me?")
    #     self.assertTemplateUsed(response, 'index.html')

    def test_upcoming_sessions(self):
        response = self.client.get(reverse('studybuddy:upcomingSessions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_rooms(self):
        response = self.client.get(reverse('studybuddy:rooms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')

    def test_room(self):
        response = self.client.get(reverse('studybuddy:room', args=(TEST_PK,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Do you want to study with me?")
        self.assertTemplateUsed(response, 'index.html')
