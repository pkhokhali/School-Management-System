from rest_framework import serializers
from .models import ChatRoom, Feedback, Forum, ForumPost, LiveClass, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender']


class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = '__all__'


class ForumPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = '__all__'
        read_only_fields = ['author']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['user']


class LiveClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveClass
        fields = '__all__'
