from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Author, Book, Member, BorrowRecord,BookImage
from .serializers import AuthorSerializer, BookSerializer, MemberSerializer, BorrowRecordSerializer,BookImageSerializer
from .filters import BookFilter
from .paginations import DefaultPagination
from rest_framework.permissions import IsAdminUser,AllowAny,IsAuthenticated
from api.permissions import IsAdminOrReadOnly
from drf_yasg.utils import swagger_auto_schema

class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    search_fields = ['name', 'biography']
    ordering_fields = ['name', 'updated_at']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination
    permission_classes=[IsAdminOrReadOnly]
    @swagger_auto_schema(
        operation_summary="Retrieve all authors",
        responses={200: AuthorSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new author",
        request_body=AuthorSerializer,
        responses={201: AuthorSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter 
    search_fields = ['title', 'isbn', 'category', 'author__name']
    ordering_fields = ['price', 'Book_pages', 'updated_at']
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Book.objects.prefetch_related('images').all()
    
    @swagger_auto_schema(
        operation_summary='Retrive a list of book'
    )
    def list(self, request, *args, **kwargs):
        """Retrive all the book"""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create a book by admin",
        operation_description="This allow an admin to create a book",
        request_body=BookSerializer,
        responses={
            201: BookSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        if book.availability_status == Book.UNAVAILABLE:
            return Response({'message': "Cannot delete unavailable book"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(book)
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookImagesViewSet(ModelViewSet):
    serializer_class=BookImageSerializer
    permission_classes=[IsAuthenticated]
    permission_classes=[IsAdminOrReadOnly]

    def get_queryset(self):
        book_pk = self.kwargs.get('book_pk')
        return BookImage.objects.filter(book_id=book_pk)
    
    @swagger_auto_schema(
        operation_summary="Upload an image for a book",
        request_body=BookImageSerializer,
        responses={201: BookImageSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        book_pk = self.kwargs.get('book_pk')
        book = Book.objects.get(pk=book_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(book=book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    search_fields = ['name', 'email']
    ordering_fields = ['membership_date', 'updated_at']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination

    @swagger_auto_schema(
        operation_summary="Retrieve all members",
        responses={200: MemberSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create a new member",
        request_body=MemberSerializer,
        responses={201: MemberSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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
    
    @swagger_auto_schema(
        operation_summary="Retrieve all borrow records",
        responses={200: BorrowRecordSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a borrow record",
        request_body=BorrowRecordSerializer,
        responses={201: BorrowRecordSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
