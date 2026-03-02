from django.contrib import admin
from .models import UserProfile, DailyLog, WeeklySummary


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'supervisor', 'total_required_hours', 'ojt_start_date']
    search_fields = ['user__username', 'user__first_name', 'department', 'supervisor']
    list_filter = ['department']


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['profile', 'date', 'week_number', 'time_in', 'time_out', 'daily_hours']
    list_filter = ['profile__department', 'week_number']
    search_fields = ['profile__user__username', 'remarks']
    ordering = ['-date']
    readonly_fields = ['daily_hours', 'week_number']


@admin.register(WeeklySummary)
class WeeklySummaryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'week_number', 'updated_at']
    list_filter = ['profile__department']
    search_fields = ['profile__user__username']
