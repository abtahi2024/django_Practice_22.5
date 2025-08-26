from django.urls import path, include
from libarayapp.views import AuthorViewSet,BookViewSet,BorrowRecordViewSet,MemberViewSet
# from order.views import CartViewSet, CartItemViewSet
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('authors', AuthorViewSet, basename='authors')
router.register('books', BookViewSet, basename='books')
router.register('members', MemberViewSet, basename='members')

author_router = routers.NestedDefaultRouter(router, 'authors', lookup='author')
author_router.register('books', BookViewSet, basename='author-books')


member_router = routers.NestedDefaultRouter(router, 'members', lookup='member')
member_router.register('borrow-records', BorrowRecordViewSet, basename='member-borrow-records')

book_router = routers.NestedDefaultRouter(router, 'books', lookup='book')
book_router.register('borrow-records', BorrowRecordViewSet, basename='book-borrow-records')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(author_router.urls)),
    path('', include(member_router.urls)),
    path('', include(book_router.urls)),
]