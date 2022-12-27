from django.shortcuts import render
from studybuddy.models import User, Friend_Request


def send_friend_request(request, requestee_email):
    '''
    return 0: friend request was already sent and is pending approval
           1: friend request was created and sent
           2: the 2 users are already friends
    '''

    # This method is called after already processing to and from users are valid
    from_user = User.objects.get(email__exact=request.user.email)
    to_user = User.objects.get(email__exact=requestee_email)

    if from_user.friends.all().filter(email=requestee_email):
        return 2

    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        return 1
    else:
        return 0


def accept_friend_request(request, requester_email):
    """
    return 0: friend request doesn't exist/already accepted
           1: friend request successfully accepted
    """
    from_user = User.objects.get(email=requester_email)
    to_user = User.objects.get(email=request.user.email)

    friend_request_query_set = Friend_Request.objects.filter(from_user=from_user).filter(to_user=to_user)
    friend_request = friend_request_query_set.first()

    if friend_request:
        friend_request.to_user.friends.add(friend_request.from_user)
        print(friend_request.to_user.friends.all())
        friend_request.from_user.friends.add(friend_request.to_user)
        print(friend_request.from_user.friends.all())
        friend_request.delete()
        return 1
    else:
        return 0


def remove_friend(request, email):
    User.objects.get(email=request.user.email).friends.remove(User.objects.get(email=email))


def decline_request(request, email):
    """
    this method is called with the request.user is trying to delete a friend request
    parameters: email - the email of the user that sent the friend request
    """
    from_user = User.objects.get(email=email)
    to_user = User.objects.get(email=request.user.email)

    Friend_Request.objects.filter(from_user=from_user).filter(to_user=to_user).delete()


def view_friends(request):
    if request.user.is_anonymous:
        return render(request, template_name="index.html")

    from_user = User.objects.get(email=request.user.email)
    # get the friend requests that are sent to the current user
    friend_request = Friend_Request.objects.filter(to_user=from_user)
    sent_requests = Friend_Request.objects.filter(from_user=from_user)
    friends = from_user.friends.all()

    context = {
        'friends': friends,
        'friend_requests': friend_request,
        'sent_requests': sent_requests,
        'student_name': from_user.name,
        # add declined?
    }

    if from_user.name == "":
        context['student_name'] = request.user

    # if the user sent a friend request
    if request.POST.get('request'):
        requestee_email = request.POST.get('email')
        context['toEmail'] = requestee_email
        # make sure the user isn't trying to add themselves
        if requestee_email == request.user.email:
            context['self'] = True
        # check that the requested friend is in our system
        elif User.objects.filter(email__exact=requestee_email).exists():
            # send the request (adds to friend_request model)
            send = send_friend_request(request, requestee_email)

            # if returned 1, means the friend request was created
            if send == 1:
                context['sent'] = True
            elif send == 2:
                context['already_friends'] = True
            # else it returned a 0 meaning the friend request was already pending
            else:
                context['alreadySent'] = True

        # if the user isn't in our system let the user know
        else:
            context['notValid'] = True

    # user accepted a friend request
    if request.POST.get('accept'):
        ad_email = request.POST.get('ad_email')
        accepted = accept_friend_request(request, ad_email)
        if accepted:
            context['accepted'] = True
            context['accepted_email'] = ad_email

    if request.POST.get('decline'):
        ad_email = request.POST.get('ad_email')
        decline_request(request, ad_email)
        context['declined'] = True
        context['declined_email'] = ad_email

    if request.POST.get('unfriend'):
        remove_email = request.POST.get('remove_email')
        remove_friend(request, remove_email)
        context['remove_friend'] = True
        context['removed_email'] = remove_email

    if request.POST.get('view_friends'):
        friend_email = request.POST.get('friend_email')
        request.POST = None
        return view_friend_profile(request, friend_email)

    request.POST = None
    return render(request, "friends/view_friends.html", context)


def view_friend_profile(request, friend_email):
    friend = User.objects.get(email__exact=friend_email)

    context = {
        'student': User.objects.get(email=request.user.email),
        'student_name': User.objects.get(email=request.user.email).name,
        'friend': friend
    }

    if User.objects.get(email=request.user.email).name == "":
        context['student_name'] = request.user

    return render(request, "friends/friend_profile.html", context)
