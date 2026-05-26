from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, FeedbackViewSet, ForumPostViewSet, ForumViewSet, LiveClassViewSet, MessageViewSet

router = DefaultRouter()
router.register('rooms', ChatRoomViewSet, basename='chat-room')
router.register('messages', MessageViewSet, basename='message')
router.register('forums', ForumViewSet, basename='forum')
router.register('forum-posts', ForumPostViewSet, basename='forum-post')
router.register('feedback', FeedbackViewSet, basename='feedback')
router.register('live-classes', LiveClassViewSet, basename='live-class')
urlpatterns = [path('', include(router.urls))]
