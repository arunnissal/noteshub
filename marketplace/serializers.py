from rest_framework import serializers
from .models import Account, UserProfile, Subject, Note, Wishlist, Review, Order

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'phone', 'name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_name', 'phone', 'student_id', 'college', 'department', 
            'year', 'bio', 'rating', 'total_sales', 'total_purchases', 'created_at'
        ]
        read_only_fields = ['id', 'rating', 'total_sales', 'total_purchases', 'created_at']

class NoteSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    seller_phone = serializers.CharField(source='seller.phone', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    in_wishlist = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'description', 'price', 'semester', 'year', 'tags',
            'contact_info', 'views', 'downloads', 'is_free', 'is_approved',
            'created_at', 'updated_at', 'seller_name', 'seller_phone',
            'subject_name', 'subject_code', 'in_wishlist', 'avg_rating', 'review_count'
        ]
        read_only_fields = [
            'id', 'views', 'downloads', 'is_approved', 'created_at', 'updated_at',
            'seller_name', 'seller_phone', 'subject_name', 'subject_code',
            'in_wishlist', 'avg_rating', 'review_count'
        ]
    
    def get_in_wishlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, note=obj).exists()
        return False
    
    def get_avg_rating(self, obj):
        reviews = Review.objects.filter(note=obj)
        if reviews.exists():
            from django.db.models import Avg
            return round(reviews.aggregate(avg=Avg('rating'))['avg'], 2)
        return 0.00
    
    def get_review_count(self, obj):
        return Review.objects.filter(note=obj).count()

class WishlistSerializer(serializers.ModelSerializer):
    note = NoteSerializer(read_only=True)
    note_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'note', 'note_id', 'created_at']
        read_only_fields = ['id', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.name', read_only=True)
    note_title = serializers.CharField(source='note.title', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'comment', 'created_at', 
            'reviewer_name', 'note_title'
        ]
        read_only_fields = ['id', 'created_at', 'reviewer_name', 'note_title']

class OrderSerializer(serializers.ModelSerializer):
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    note_title = serializers.CharField(source='note.title', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'amount', 'status', 'payment_method', 'transaction_id',
            'created_at', 'completed_at', 'buyer_name', 'seller_name', 'note_title'
        ]
        read_only_fields = [
            'id', 'created_at', 'completed_at', 'buyer_name', 'seller_name', 'note_title'
        ]

# Dashboard Serializers
class DashboardStatsSerializer(serializers.Serializer):
    total_notes = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    wishlist_count = serializers.IntegerField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2)

class ActivitySerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField()

class TopNoteSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'price', 'views', 'subject_name', 'avg_rating',
            'contact_info', 'is_free'
        ]
    
    def get_avg_rating(self, obj):
        reviews = Review.objects.filter(note=obj)
        if reviews.exists():
            from django.db.models import Avg
            return round(reviews.aggregate(avg=Avg('rating'))['avg'], 2)
        return 0.00

# Analytics Serializers
class AnalyticsSerializer(serializers.Serializer):
    recent_notes = serializers.IntegerField()
    total_views = serializers.IntegerField()
    popular_subjects = serializers.ListField()

class PopularSubjectSerializer(serializers.Serializer):
    subject__name = serializers.CharField()
    count = serializers.IntegerField() 