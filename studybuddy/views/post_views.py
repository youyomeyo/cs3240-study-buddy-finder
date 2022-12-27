from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render
from studybuddy.models import Post, Course, User, EnrolledClass


def makepost(request, dept, course_number):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    template_name = 'post/makepost.html'

    context = {
        'dept': dept.upper(),
        'course_number': course_number,
        'student_name': User.objects.get(email=request.user.email).name,
    }

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    if Course.objects.filter(course_number=course_number, subject=dept.upper()).exists():
        context['course'] = Course.objects.get(course_number=course_number)

    return render(request, template_name, context)


def submitpost(request, dept, course_number):
    email = request.user.email
    print('here')
    # if the course exists
    if Course.objects.filter(course_number=course_number, subject=dept.upper()).exists():
        course = Course.objects.get(course_number=course_number)

        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        topic = request.POST['topic']
        description = request.POST['description']

        # If user chooses to not provide values, then the default values will be used
        if start_date == "":
            start_date = Post._meta.get_field('startDate').get_default()

        print(end_date)
        if end_date == "":
            end_date = Post._meta.get_field('endDate').get_default()

        if topic == "":
            topic = Post._meta.get_field('topic').get_default()

        if description == "":
            description = Post._meta.get_field('description').get_default()

        user = User.objects.get(email=email)
        author = str(request.user)
        if user.name != "":
            author = user.name

        # Get if user wants post to be in specific section or all sections of catalog_number
        # Default: post to only this specific section
        if request.POST['post_type'] == 'section':
            newPost = Post(course=course,
                           user=user,
                           # right now if User.objects doesn't have a name it will be empty, so this will ensure we have name?
                           author=author,
                           topic=topic,
                           startDate=start_date,
                           endDate=end_date,
                           description=description,
                           post_type='section')
            newPost.save()
        else:
            newPost = Post(course=course,
                           user=user,
                           # right now if User.objects doesn't have a name it will be empty, so this will ensure we have name?
                           author=author,
                           topic=topic,
                           startDate=start_date,
                           endDate=end_date,
                           description=description,
                           post_type='course')
            newPost.save()

        return 1
    else:
        return 0


def deletepost(request):
    email = request.user.email
    target_post_pk = request.POST['post_pk']
    # There shouldn't be a case where this called and post_pk doesn't exist because this is
    # method and not a url call. Putting in guards just in case
    if Post.objects.filter(user=User.objects.get(email=email), pk=target_post_pk).exists():
        Post.objects.get(user=User.objects.get(email=email), pk=target_post_pk).delete()


def viewposts(request):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    if request.POST.get('delete'):
        deletepost(request)

    Post.objects.filter(endDate__lt=timezone.localtime()).delete()

    email = request.user.email
    template_name = 'post/viewposts.html'
    user_posts = Post.objects.filter(user=User.objects.get(email=email)).distinct()
    enrolled_courses = EnrolledClass.objects.filter(student=User.objects.get(email=email))
    unenrolled_posts_pk = []

    for post in user_posts:
        if not enrolled_courses.filter(course=post.course).exists():
            # if the student is not enrolled in the class append the post pk
            unenrolled_posts_pk.append(post.pk)

    unenrolled_posts = None
    for pk in unenrolled_posts_pk:
        if unenrolled_posts is None:
            unenrolled_posts = Post.objects.filter(pk=pk)
        else:
            unenrolled_posts = unenrolled_posts | Post.objects.filter(pk=pk)

    context = {
        'user_posts': user_posts,
        'enrolled_courses': enrolled_courses,
        'student_name': User.objects.get(email=request.user.email).name,
    }

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    if enrolled_courses.count() == 0 and unenrolled_posts is None:
        context['no_courses_and_post'] = True

    if unenrolled_posts is not None:
        context['unenrolled_posts'] = unenrolled_posts

    request.POST = None
    return render(request, template_name, context)
