from django.contrib import admin
from .models import Comments, Category, Complaint



admin.site.register(Complaint)
admin.site.register(Comments)
admin.site.register(Category)
