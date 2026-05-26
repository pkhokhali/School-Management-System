from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.mixins import FeatureFlagViewMixin
from rest_framework import serializers
from .models import Book, BookIssue


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookIssue
        fields = '__all__'


class LibraryMixin(FeatureFlagViewMixin):
    feature_key = 'library_management'


class BookViewSet(LibraryMixin, viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class BookIssueViewSet(LibraryMixin, viewsets.ModelViewSet):
    queryset = BookIssue.objects.select_related('book', 'student')
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]
