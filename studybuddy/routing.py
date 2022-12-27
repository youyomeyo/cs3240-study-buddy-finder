# Source: https://stackoverflow.com/questions/54107099/django-channels-no-route-found-for-path

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'studybuddy/chat/rooms/(?P<room_name>[^/]+)/', consumers.ChatConsumer.as_asgi()),
]