import requests, json
from studybuddy.views import room_views, post_views
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect
from studybuddy.models import User, Departments, Course, Post, EnrolledClass, Room


def index(request):
    if request.user.is_anonymous or not User.objects.filter(email=request.user.email).exists():
        return render(request, template_name="index.html")
    else:
        template_name = 'homepage.html'

        context = {
            'student_name': User.objects.get(email=request.user.email).name,
            'student': User.objects.get(email=request.user.email)
        }

        if User.objects.get(email=request.user.email).name == "":
            context['student_name'] = request.user

        return render(request, template_name, context)


def addAccount(request):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    email = request.user.email
    exist = User.objects.filter(email=email).exists()
    if not exist:
        newAcc = User.objects.create(email=email, name=request.user.username)
        # newAcc.save()
        return HttpResponseRedirect(reverse('studybuddy:editAccount'))
    else:
        return HttpResponseRedirect(reverse('studybuddy:index'))


def account(request):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    email = request.user.email
    user = User.objects.get(email__exact=email)
    context = {
        'Email': user.email,
        'UserName': user.username,
        'Name': user.name,
        'Major': user.major,
        'ZoomLink': user.zoomLink,
        'Introduction': user.blurb,
        'student': user,
        'student_name': user.name
    }

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    return render(request, 'studybuddy/account.html', context)


def EditAccount(request):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    email = request.user.email
    user = User.objects.get(email=email)
    context = {
        'Email': user.email,
        'UserName': user.username,
        'Name': user.name,
        'Major': user.major,
        'ZoomLink': user.zoomLink,
        'Introduction': user.blurb,
        'student_name': User.objects.get(email=email).name,
    }

    if User.objects.get(email=email).name == "":
        context['student_name'] = request.user

    return render(request, 'studybuddy/editAccount.html', context)


def UpdateAccount(request):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    email = request.user.email
    account = User.objects.get(email__exact=email)
    account.username = request.POST['username']
    account.name = request.POST['name']
    account.major = request.POST['major']
    account.zoomLink = request.POST['zlink']
    account.blurb = request.POST['blurb']

    account.save()

    return HttpResponseRedirect(reverse('studybuddy:account'))


class alldepartments(generic.ListView):
    model = Departments
    # template_name = get_template_name()

    # Get the json for all the departments
    deptList = requests.get('http://luthers-list.herokuapp.com/api/deptlist/')
    deptList_json = json.loads(deptList.text)

    # makes sure there are no departments from previous calls
    if Departments.objects.exists():
        Departments.objects.all().delete()

    # Get all of the current departments available
    for i in range(len(deptList_json)):
        newDept = Departments(dept=deptList_json[i].get("subject"))
        newDept.save()

    def get_queryset(self):
        return Departments.objects.all()

    # Source: https://stackoverflow.com/questions/9899113/get-request-session-from-a-class-based-generic-view
    def get_context_data(self, *args, **kwargs):
        context = super(alldepartments, self).get_context_data(*args, **kwargs)
        if not self.request.user.is_anonymous:
            context['student_name'] = User.objects.get(email=self.request.user.email).name
            if User.objects.get(email=self.request.user.email).name == "":
                context['student_name'] = self.request.user
        return context

    def get_template_names(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return 'index.html'
        return 'alldepartments.html'


def department(request, dept):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    if dept == "viewpost":
        return post_views.viewposts(request)

    template_name = 'department.html'

    # Get the json file for the request department
    dept = dept.upper()
    dept_request = "http://luthers-list.herokuapp.com/api/dept/" + dept
    dept_classes = requests.get(dept_request)
    dept_classes_json = json.loads(dept_classes.text)

    # Get all of the classes in the requested department
    for i in range(len(dept_classes_json)):
        current_class = dept_classes_json[i]

        # if the course doesn't exists then we will add it
        if not Course.objects.filter(subject=dept,
                                     catalog_number=current_class.get('catalog_number'),
                                     instructor=current_class.get('instructor').get('name'),
                                     section=current_class.get('course_section'),
                                     course_number=current_class.get('course_number'),
                                     description=current_class.get('description')).exists():
            newClass = Course(subject=dept,
                              catalog_number=current_class.get('catalog_number'),
                              instructor=current_class.get('instructor').get('name'),
                              section=current_class.get('course_section'),
                              course_number=current_class.get('course_number'),
                              description=current_class.get('description'))
            newClass.save()

    context = {
        'student_name': User.objects.get(email=request.user.email).name,
        'department_list': Course.objects.filter(subject=dept),
        'dept': dept
    }

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    return render(request, template_name, context)


def coursefeed(request, dept, course_number):
    template_name = 'course_feed.html'

    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    if request.POST.get('delete'):
        post_views.deletepost(request)

    if request.POST.get('message'):
        return room_views.room(request, room_views.addRoom(request))

    if request.POST.get('submit'):
        post_views.submitpost(request, dept, course_number)
        return HttpResponseRedirect(reverse('studybuddy:coursefeed', args=(dept, course_number)))

    if request.GET.get('leave'):
        room_pk = request.GET['room_pk']
        if Room.objects.filter(pk=room_pk):
            room = Room.objects.get(pk=room_pk)
            if room.users.count() == 1:
                room.delete()
            else:
                room.users.remove(User.objects.get(email=request.user.email))
        return HttpResponseRedirect(reverse('studybuddy:rooms'))

    email = request.user.email
    context = {
        'dept': dept.upper(),
        'student_name': User.objects.get(email=email).name,
    }

    if Course.objects.filter(course_number=course_number).exists() and Course.objects.filter(subject=dept):
        course = Course.objects.get(course_number=course_number)
        Post.objects.filter(endDate__lt=timezone.localtime()).delete()
        post_for_this_class = Post.objects.filter(
            course=course)  # this will find posts that are related to this specific section only

        for catalog_course in Course.objects.filter(subject=course.subject, catalog_number=course.catalog_number):
            post_for_this_class = post_for_this_class | Post.objects.filter(course=catalog_course, post_type='course')

        context['course'] = course
        context['valid'] = 'true'
        context['feed_posts'] = post_for_this_class
        context['has_posts'] = post_for_this_class.exists()
        context['enrolled'] = EnrolledClass.objects.filter(course=Course.objects.get(course_number=course_number),
                                                     student=User.objects.get(email=email)).exists()

    else:
        context['course_number'] = course_number

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    return render(request, template_name, context)


def enrollcourse(request, dept, course_number):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    template_name = 'enroll.html'

    context = {
        'student_name': User.objects.get(email=request.user.email).name,
        'dept': dept.upper(),
    }

    if Course.objects.filter(course_number=course_number).exists():
        context['course'] = Course.objects.get(course_number=course_number)
        context['valid'] = 'true'
        context['enrolled'] = EnrolledClass.objects.filter(course=Course.objects.get(course_number=course_number),
                                                     student=User.objects.get(email=request.user.email)).exists()
    else:
        context['course'] = course_number

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    return render(request, template_name, context)


def updatecourseload(request, dept, course_number):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    email = request.user.email
    account = User.objects.get(email__exact=email)
    course = Course.objects.get(course_number=course_number)

    action = request.POST['choice']
    if action == "YesD":
        EnrolledClass.objects.filter(course=course, student=account).delete()
    elif action == "YesE" and not EnrolledClass.objects.filter(course=course, student=account).exists():
        enrolled = EnrolledClass(course=course, student=account)
        enrolled.save()

    return HttpResponseRedirect(reverse('studybuddy:index'))
