import datetime
from django.db import models
from django.utils import timezone


# Create your models here.
class User(models.Model):
    email = models.CharField(primary_key=True, max_length=30, default="")
    # firstName = models.CharField(max_length=30, default="")
    # lastName = models.CharField(max_length=30, default="")
    username = models.CharField(max_length=30, default="")
    name = models.CharField(max_length=50, default="")
    major = models.CharField(max_length=50, default="")
    zoomLink = models.URLField(max_length=300, default="")
    blurb = models.TextField(default="")

    # implementing friends
    friends = models.ManyToManyField("self")
    username = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.email


# implementing friends
class Friend_Request(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    declined = models.TextField('no')

    def __str__(self):
        return self.from_user.email


class Departments(models.Model):
    dept = models.CharField(max_length=4)

    def __str__(self):
        return self.dept


class Course(models.Model):
    subject = models.CharField(max_length=4)
    catalog_number = models.CharField(max_length=4)
    instructor = models.CharField(max_length=100)
    section = models.CharField(max_length=4)
    course_number = models.CharField(max_length=10)
    description = models.TextField(default="")

    class Meta:
        unique_together = ["subject", "catalog_number", "instructor", "section", "course_number", "description"]

    def class_str(self):
        course_level = self.subject + str(self.catalog_number)
        return course_level + ": " + self.description

    def __str__(self):
        course_level = self.subject + str(self.catalog_number)
        if self.instructor == '-':
            inst = "Not available"
        else:
            inst = self.instructor
        instructor = "Instructor: " + inst
        section = "(Section: " + str(self.section) + ")"
        return course_level + ": " + self.description + " \n " + instructor + " \n " + section


class Post(models.Model):
    """
    Foreign Key means: one post can only be related to more than one course
    we want this so we can relate posts to more than one section

    Note: change to models.OneToOneField if we want to have a post only be related to one course

    Source for on_delete: https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models
        we want to remove posts related to the course and/or user when a post is delete, so we are using using CASCADE
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, )
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    author = models.CharField(max_length=30, default="Author of this post chose to be anonymous")
    topic = models.CharField(max_length=100, default="No topic was provided by the author of this post")
    startDate = models.DateField(default=timezone.now().strftime("%Y-%m-%d"))
    endDate = models.DateField(default=(timezone.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
    description = models.TextField(default="No description was provided by the author of this post")
    post_type = models.TextField(default="section")

    def past_end_date(self):
        now = timezone.now()
        # returns true if endDate has passed
        # returns false if endDate is still valid
        return now > self.endDate

    def __str__(self):
        author = "Author: " + self.author
        if type(self.startDate) != str:
            time_frame = self.startDate.strftime("%m-%d-%Y") + " to " + self.endDate.strftime(
                "%m-%d-%Y")
        else:
            time_frame = self.startDate + " to " + self.endDate

        return self.topic + '\n' + author + '\n' + time_frame + '\n'


class EnrolledClass(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.subject + " " + self.course.course_number


class Room(models.Model):
    name = models.CharField(max_length=255)
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)

    def __str__(self):
        course_name = self.post.course.subject + str(self.post.course.catalog_number)
        course_description = self.post.course.description
        topic = 'Topic: ' + self.name
        # return course_name + ': ' + course_description + '\n' + topic
        return course_name + ' - ' + self.name


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)


class StudySession(models.Model):
    """
    a study session is associated with a post
    """
    # if post is deleted, the study session should still remain, because deletion of a post means
    # the user no longer wants the post/they have found a study buddy, but study sessions schedule should remain
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    users = models.ManyToManyField(User)
    # If the author of the study session is removed the system, their study sessions should also be removed
    author = models.CharField(max_length=100)

    # currently just setting it the room name
    name = models.CharField(max_length=50, default="Study Session")  # update after figuring out room/post/user relation
    date = models.DateField(default=timezone.now().strftime("%m-%d-%Y"))
    start = models.TimeField(default=timezone.now().strftime("%H-%M"))
    end = models.TimeField(default=(timezone.now() + datetime.timedelta(hours=1)).strftime("%H-%M"))
    accepted = models.CharField(max_length=4, default="?")

    def __str__(self):
        if type(self.start) != str:
            time_frame = "Time Frame: " + self.start.strftime("%H:%M") + " to " + self.end.strftime("%H:%M")
        else:
            time_frame = "Time Frame: " + self.start + " to " + self.start

        if type(self.date) != str:
            date = "Scheduled on: " + self.date.strftime("%m-%d-%Y")
        else:
            date = "Scheduled on: " + self.date

        name = "Study session for: " + self.name

        return name + '\n' + date + '\n' + time_frame
