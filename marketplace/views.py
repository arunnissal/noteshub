from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Account, UserProfile, Subject, Note, Wishlist, Review
from .serializers import (
    AccountSerializer, UserProfileSerializer, SubjectSerializer, 
    NoteSerializer, WishlistSerializer
)
# OTP-related code removed. Only password-based authentication remains.
import random
import string

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user with phone number and password
    """
    phone = request.data.get('phone')
    password = request.data.get('password')
    name = request.data.get('name', '')
    
    if not phone or not password:
        return Response({
            'error': 'Phone number and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already exists
    if Account.objects.filter(phone=phone).exists():
        return Response({
            'error': 'User with this phone number already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Create user
            user = Account.objects.create_user(
                phone=phone,
                password=password,
                name=name
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': AccountSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': f'Registration failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user with phone number and password
    """
    phone = request.data.get('phone')
    password = request.data.get('password')
    
    if not phone or not password:
        return Response({
            'error': 'Phone number and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(phone=phone, password=password)
    
    if user is None:
        return Response({
            'error': 'Invalid phone number or password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'Account is disabled'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': AccountSerializer(user).data,
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_profile(request):
    """
    Create or update user profile
    """
    user = request.user
    
    # Check if profile already exists
    if hasattr(user, 'profile'):
        return Response({
            'error': 'Profile already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            profile = UserProfile.objects.create(
                user=user,
                student_id=request.data.get('student_id'),
                college=request.data.get('college'),
                department=request.data.get('department'),
                year=request.data.get('year'),
                phone=user.phone,
                bio=request.data.get('bio', '')
            )
            
            return Response({
                'message': 'Profile created successfully',
                'profile': UserProfileSerializer(profile).data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': f'Profile creation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def subject_list(request):
    """
    Get list of all subjects
    """
    subjects = Subject.objects.all()
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_note(request):
    """
    Create a new note listing
    """
    try:
        with transaction.atomic():
            note = Note.objects.create(
                seller=request.user,
                subject_id=request.data.get('subject'),
                title=request.data.get('title'),
                description=request.data.get('description'),
                price=request.data.get('price', 0.00),
                semester=request.data.get('semester'),
                year=request.data.get('year'),
                tags=request.data.get('tags', ''),
                contact_info=request.data.get('contact_info', ''),
                is_free=request.data.get('is_free', True)
            )
            
            return Response({
                'message': 'Note created successfully',
                'note': NoteSerializer(note).data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'error': f'Note creation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def note_list(request):
    """
    Get list of all notes with advanced filtering and search
    """
    notes = Note.objects.filter(is_approved=True)
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(subject__name__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # Subject filter
    subject = request.GET.get('subject', '')
    if subject:
        notes = notes.filter(subject_id=subject)
    
    # Semester filter
    semester = request.GET.get('semester', '')
    if semester:
        notes = notes.filter(semester=semester)
    
    # Price range filter
    price_range = request.GET.get('price_range', '')
    if price_range:
        if price_range == 'free':
            notes = notes.filter(is_free=True)
        elif price_range == '0-100':
            notes = notes.filter(price__gte=0, price__lte=100, is_free=False)
        elif price_range == '100-500':
            notes = notes.filter(price__gte=100, price__lte=500, is_free=False)
        elif price_range == '500+':
            notes = notes.filter(price__gte=500, is_free=False)
    
    # Add wishlist status for authenticated users
    if request.user.is_authenticated:
        for note in notes:
            note.in_wishlist = Wishlist.objects.filter(user=request.user, note=note).exists()
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = 12
    start = (page - 1) * page_size
    end = start + page_size
    
    total_count = notes.count()
    notes_page = notes[start:end]
    
    serializer = NoteSerializer(notes_page, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'next': f'/api/notes/?page={page + 1}' if end < total_count else None,
        'previous': f'/api/notes/?page={page - 1}' if page > 1 else None,
        'current_page': page,
        'total_pages': (total_count + page_size - 1) // page_size
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    """
    Add a note to user's wishlist
    """
    note_id = request.data.get('note_id')
    
    if not note_id:
        return Response({
            'error': 'Note ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        note = Note.objects.get(id=note_id)
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=request.user, note=note).exists():
            return Response({
                'error': 'Note already in wishlist'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        wishlist_item = Wishlist.objects.create(
            user=request.user,
            note=note
        )
        
        return Response({
            'message': 'Added to wishlist successfully',
            'wishlist_item': WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED)
        
    except Note.DoesNotExist:
        return Response({
            'error': 'Note not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Failed to add to wishlist: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wishlist_list(request):
    """
    Get user's wishlist
    """
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('note', 'note__subject')
    
    # Add subject name to note data
    for item in wishlist_items:
        item.note.subject_name = item.note.subject.name
    
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request, wishlist_id):
    """
    Remove a note from user's wishlist
    """
    try:
        wishlist_item = Wishlist.objects.get(id=wishlist_id, user=request.user)
        wishlist_item.delete()
        
        return Response({
            'message': 'Removed from wishlist successfully'
        }, status=status.HTTP_200_OK)
        
    except Wishlist.DoesNotExist:
        return Response({
            'error': 'Wishlist item not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or create user profile
    """
    user = request.user
    
    try:
        profile = user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)

# New Dashboard Endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for the user
    """
    user = request.user
    
    # Get user's notes count
    total_notes = Note.objects.filter(seller=user).count()
    
    # Get total sales (this would be calculated from orders in a real app)
    total_sales = 0  # Placeholder for now
    
    # Get wishlist count
    wishlist_count = Wishlist.objects.filter(user=user).count()
    
    # Get average rating from reviews
    avg_rating = Review.objects.filter(seller=user).aggregate(Avg('rating'))['rating__avg'] or 0.00
    
    return Response({
        'total_notes': total_notes,
        'total_sales': total_sales,
        'wishlist_count': wishlist_count,
        'rating': round(avg_rating, 2)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_activity(request):
    """
    Get recent activity for the user
    """
    user = request.user
    
    # Get recent notes created
    recent_notes = Note.objects.filter(seller=user).order_by('-created_at')[:5]
    
    # Get recent wishlist additions
    recent_wishlist = Wishlist.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Combine and sort activities
    activities = []
    
    for note in recent_notes:
        activities.append({
            'type': 'note_created',
            'title': f'Created note: {note.title}',
            'created_at': note.created_at
        })
    
    for wishlist_item in recent_wishlist:
        activities.append({
            'type': 'wishlist_added',
            'title': f'Added to wishlist: {wishlist_item.note.title}',
            'created_at': wishlist_item.created_at
        })
    
    # Sort by creation date
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    
    return Response(activities[:10])  # Return top 10 activities

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_top_notes(request):
    """
    Get top rated notes for the dashboard
    """
    # Get notes with highest ratings
    top_notes = Note.objects.filter(is_approved=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating', '-views')[:10]
    
    # Add subject names
    for note in top_notes:
        note.subject_name = note.subject.name
    
    serializer = NoteSerializer(top_notes, many=True)
    return Response(serializer.data)

# Enhanced Search Endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def search_notes(request):
    """
    Advanced search functionality
    """
    query = request.GET.get('q', '')
    subject = request.GET.get('subject', '')
    semester = request.GET.get('semester', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    year = request.GET.get('year', '')
    
    notes = Note.objects.filter(is_approved=True)
    
    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(tags__icontains=query)
        )
    
    if subject:
        notes = notes.filter(subject_id=subject)
    
    if semester:
        notes = notes.filter(semester=semester)
    
    if year:
        notes = notes.filter(year=year)
    
    if price_min:
        notes = notes.filter(price__gte=float(price_min))
    
    if price_max:
        notes = notes.filter(price__lte=float(price_max))
    
    # Add wishlist status for authenticated users
    if request.user.is_authenticated:
        for note in notes:
            note.in_wishlist = Wishlist.objects.filter(user=request.user, note=note).exists()
    
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)

# Analytics Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics(request):
    """
    Get analytics data for the user
    """
    user = request.user
    
    # Notes created in last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_notes = Note.objects.filter(seller=user, created_at__gte=thirty_days_ago).count()
    
    # Views on user's notes
    total_views = Note.objects.filter(seller=user).aggregate(Sum('views'))['views__sum'] or 0
    
    # Popular subjects
    popular_subjects = Note.objects.filter(seller=user).values('subject__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    return Response({
        'recent_notes': recent_notes,
        'total_views': total_views,
        'popular_subjects': popular_subjects
    })
