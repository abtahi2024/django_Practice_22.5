from rest_framework import serializers
from libarayapp.models import Author,Book,Member,BorrowRecord,BookImage
from decimal import Decimal
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Author

        fields=['id','name','biography','create_at','updated_at']

class BookImageSerializer(serializers.ModelSerializer):
    image=serializers.ImageField(use_url=True)
    class Meta:
        model = BookImage
        fields = ['id','book', 'image']

class BookSerializer(serializers.ModelSerializer):
    author=AuthorSerializer(read_only=True)
    author_id=serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(),source='author',write_only=True)  #Write-only field দিয়ে foreign key assign করা

    price_with_tex=serializers.SerializerMethodField(method_name='calculate_tex')

    images=BookImageSerializer(many=True,read_only=True)
    class Meta:
        model=Book
        fields=[
            'id', 'title', 'author', 'author_id', 'isbn', 'category',
            'availability_status', 'Book_pages', 'price', 'price_with_tex',
            'create_at', 'updated_at','images'
        ]

    def calculate_tex(self,book):
        if book.price:
            return round(book.price*Decimal(1.1),2)
        return None
    
    def validate_Book_pages(self, value):
        if value<=0:
            raise serializers.ValidationError('pages must be greater then 0')
        return value



class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'membership_date', 'create_at', 'updated_at']

class BorrowRecordSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )
    member = MemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='member', write_only=True
    )

    class Meta:
        model = BorrowRecord
        fields = [
            'id', 'book', 'book_id', 'member', 'member_id',
            'borrow_date', 'return_date', 'create_at', 'updated_at'
        ]