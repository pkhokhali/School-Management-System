from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.mixins import FeatureFlagViewMixin
from .models import ChatRoom, Feedback, Forum, ForumPost, LiveClass, Message
from .serializers import (
    ChatRoomSerializer, FeedbackSerializer, ForumPostSerializer,
    ForumSerializer, LiveClassSerializer, MessageSerializer,
)


class ChatFeatureMixin(FeatureFlagViewMixin):
    feature_key = 'in_app_chat'


class LiveClassFeatureMixin(FeatureFlagViewMixin):
    feature_key = 'live_classes'


class ChatRoomViewSet(ChatFeatureMixin, viewsets.ModelViewSet):
    queryset = ChatRoom.objects.prefetch_related('participants')
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]


class MessageViewSet(ChatFeatureMixin, viewsets.ModelViewSet):
    queryset = Message.objects.select_related('sender', 'room')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['room']

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ForumViewSet(viewsets.ModelViewSet):
    queryset = Forum.objects.select_related('course')
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]


class ForumPostViewSet(viewsets.ModelViewSet):
    queryset = ForumPost.objects.select_related('forum', 'author')
    serializer_class = ForumPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LiveClassViewSet(LiveClassFeatureMixin, viewsets.ModelViewSet):
    queryset = LiveClass.objects.select_related('course')
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]
