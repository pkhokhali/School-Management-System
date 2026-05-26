from django.conf import settings
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=20, blank=True)
    copies_total = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)


class BookIssue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
