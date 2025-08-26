from django_filters.rest_framework import FilterSet
from libarayapp.models import Book
class BookFilter(FilterSet):
    class Meta:
        model=Book
        fields={
            'category': ['exact'],
            'price': ['gt', 'lt']
        }