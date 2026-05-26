from django.contrib import admin
from .models import FeeHead, FeeStructure, Payment, RefundRequest, StudentFeeAssignment
for m in [FeeHead, FeeStructure, StudentFeeAssignment, Payment, RefundRequest]:
    admin.site.register(m)
