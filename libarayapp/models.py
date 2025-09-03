from django.db import models
from django.utils import timezone
from libarayapp.validators import validate_file_size
# Create your models here.
class TimeStampedModel(models.Model):
    create_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)  # object প্রথমবার তৈরি হলে তারিখ/সময় সেট হবে
    updated_at=models.DateTimeField(auto_now=True,null=True,blank=True) # object আপডেট হলে তারিখ/সময় আপডেট হবে

    class Meta:
        abstract=True # এর মানে এই model নিজে database এ table বানাবে না


class Author(TimeStampedModel):
    name=models.CharField()
    biography=models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Book(TimeStampedModel):
    AVAILABLE='AVAILABLE'
    UNAVAILABLE='UNAVAILABLE'
    AVAIL_CHOICES=[
        (AVAILABLE,'Available'),
        (UNAVAILABLE,'Unavailable'),
    ]

    title=models.CharField()
    author=models.ForeignKey(Author,on_delete=models.CASCADE,related_name='books')
    isbn=models.CharField(unique=True)
    category=models.CharField(max_length=100,blank=True)
    availability_status=models.CharField(max_length=50,choices=AVAIL_CHOICES,default=AVAILABLE)
    Book_pages = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f'{self.title}({self.isbn})'
    
class BookImage(TimeStampedModel):
    book=models.ForeignKey(Book,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(
        upload_to="products/images/", validators=[validate_file_size])

class Member(TimeStampedModel):
    name=models.CharField()
    email=models.EmailField(unique=True)
    membership_date=models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

class BorrowRecord(TimeStampedModel):
    BORROWED='BORROWED'
    RETURNED='RETURNED'
    STATUS_CHOICES=[
        (BORROWED,'Borrowed'),
        (RETURNED,'Returned'),
    ]

    book = models.ForeignKey(Book,on_delete=models.PROTECT,related_name='borrow_records')
    member=models.ForeignKey(Member,on_delete=models.PROTECT,related_name='borrow_records')
    borrow_date=models.DateTimeField(auto_now_add=True)
    return_date=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f'{self.book.title}->{self.member.name}'
