from django.contrib import admin
from .models import Account, Subject, UserProfile, Note, Order, Review, Wishlist
from django.contrib.auth.admin import UserAdmin

@admin.register(Account)
class AccountAdmin(UserAdmin):
    model = Account
    list_display = ['phone', 'name', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['phone', 'name']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('phone', 'password', 'name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'name', 'is_staff', 'is_superuser'),
        }),
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'college', 'department', 'year', 'rating']
    search_fields = ['user__phone', 'student_id', 'college']
    list_filter = ['year', 'department']
    ordering = ['user__phone']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'subject', 'price', 'is_free', 'is_approved', 'views', 'downloads']
    list_filter = ['is_free', 'is_approved', 'semester', 'year', 'subject']
    search_fields = ['title', 'seller__phone', 'subject__name']
    readonly_fields = ['views', 'downloads']
    ordering = ['-created_at']
    
    def approve_notes(self, request, queryset):
        queryset.update(is_approved=True)
    approve_notes.short_description = "Approve selected notes"
    
    actions = [approve_notes]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'note', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__phone', 'seller__phone', 'note__title']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'seller', 'note', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__phone', 'seller__phone', 'note__title']
    ordering = ['-created_at']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'created_at']
    search_fields = ['user__phone', 'note__title']
    ordering = ['-created_at']
