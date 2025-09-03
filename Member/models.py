from django.db import models
from users.models import Users
from libarayapp.models import Book
from uuid import uuid4
# Create your models here.

class Cart(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.first_name}"
    

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = [['cart', 'book']]

    def __str__(self):
        return f"{self.quantity} x {self.book.name}"
    
class Order(models.Model):
    NOT_PAID = 'Not Paid'
    READY_TO_SHIP = 'Ready To Ship'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELED = 'Canceled'

    STATUS_CHOICES = [
        (NOT_PAID, 'Not Paid'),
        (READY_TO_SHIP, 'Ready To Ship'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELED, 'Canceled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=NOT_PAID
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.book.name}"