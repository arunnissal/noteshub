from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    
    # User Management
    path('profile/', views.user_profile, name='user_profile'),
    
    # Subjects
    path('subjects/', views.subject_list, name='subject_list'),
    
    # Notes
    path('notes/', views.note_list, name='note_list'),
    path('notes/create/', views.create_note, name='create_note'),
    path('search/', views.search_notes, name='search_notes'),
    
    # Wishlist
    path('wishlist/', views.wishlist_list, name='wishlist_list'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/<str:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/activity/', views.dashboard_activity, name='dashboard_activity'),
    path('dashboard/top-notes/', views.dashboard_top_notes, name='dashboard_top_notes'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
] 