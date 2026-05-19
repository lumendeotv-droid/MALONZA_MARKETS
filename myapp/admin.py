
from django.contrib import admin
from .models import SiteUsers,CoursePayments,ServicePayments,Course


# Register your models here.
admin.site.register(SiteUsers)
admin.site.register(CoursePayments)
admin.site.register(ServicePayments)
admin.site.register(Course)
