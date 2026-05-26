from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    name = models.CharField(max_length=200, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Forum(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='forums')
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class ForumPost(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=50)
    target_id = models.PositiveIntegerField()
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class LiveClass(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='live_classes')
    title = models.CharField(max_length=200)
    meeting_url = models.URLField()
    provider = models.CharField(max_length=20, default='zoom')
    scheduled_at = models.DateTimeField()
