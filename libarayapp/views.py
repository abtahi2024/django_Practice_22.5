from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Author, Book, Member, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, MemberSerializer, BorrowRecordSerializer
from .filters import BookFilter
from .paginations import DefaultPagination


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    search_fields = ['name', 'biography']
    ordering_fields = ['name', 'updated_at']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter 
    search_fields = ['title', 'isbn', 'category', 'author__name']
    ordering_fields = ['price', 'Book_pages', 'updated_at']
    pagination_class = DefaultPagination

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        if book.availability_status == Book.UNAVAILABLE:
            return Response({'message': "Cannot delete unavailable book"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(book)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    search_fields = ['name', 'email']
    ordering_fields = ['membership_date', 'updated_at']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination


class BorrowRecordViewSet(ModelViewSet):
    serializer_class = BorrowRecordSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['book__title', 'member__name']
    ordering_fields = ['borrow_date', 'return_date', 'updated_at']
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = BorrowRecord.objects.all()
        book_id = self.request.query_params.get('book_id')
        member_id = self.request.query_params.get('member_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        return queryset
