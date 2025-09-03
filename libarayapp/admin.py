from django.contrib import admin
from .models import Author,Book,Member
# Register your models here.
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Member)