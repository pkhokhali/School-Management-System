from django.contrib import admin
from .models import ChatRoom, Feedback, Forum, ForumPost, LiveClass, Message
for m in [ChatRoom, Message, Forum, ForumPost, Feedback, LiveClass]:
    admin.site.register(m)
