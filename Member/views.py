from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from Member.serializers import CartSerializer, CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer
from Member.models import Cart, CartItem,Order,OrderItem
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from Member import serializers as orderSz
from rest_framework.decorators import action
from Member.services import OrderService
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
# Create your views here.


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="Create a cart for the logged-in user",
        request_body=CartSerializer,
        responses={201: CartSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve the current user's cart",
        responses={200: CartSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a cart",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    @swagger_auto_schema(
        operation_summary="Add an item to the cart",
        request_body=AddCartItemSerializer,
        responses={201: CartItemSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update a cart item quantity",
        request_body=UpdateCartItemSerializer,
        responses={200: CartItemSerializer, 400: "Bad Request"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve cart items",
        responses={200: CartItemSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Remove an item from the cart",
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self, 'swagger_fake_view', False):
            return context

        return {'cart_id': self.kwargs.get('cart_pk')}
    
    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs.get('cart_pk'))
    
class OrderViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']

    @swagger_auto_schema(
        operation_summary="Cancel an order",
        request_body=None,
        responses={200: "Order canceled"}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order=order, user=request.user)
        return Response({'status': 'Order canceled'})
    
    @swagger_auto_schema(
        operation_summary="Update order status (Admin only)",
        request_body=orderSz.UpdateOrderSerializer,
        responses={200: "Order status updated"}
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = orderSz.UpdateOrderSerializer(
            order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f'Order status updated to {request.data['status']}'})

    def get_permissions(self):
        if self.action in ['update_status', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'cancel':
            return orderSz.EmptySerializer
        if self.action == 'create':
            return orderSz.CreateOrderSerializer
        elif self.action == 'update_status':
            return orderSz.UpdateOrderSerializer
        return orderSz.OrderSerializer

    def get_serializer_context(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_serializer_context()
        return {'user_id': self.request.user.id, 'user': self.request.user}

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user=self.request.user)