from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),

    # Profile
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile_create'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Daily Logs
    path('logs/', views.DailyLogListView.as_view(), name='log_list'),
    path('logs/add/', views.DailyLogCreateView.as_view(), name='log_add'),
    path('logs/<int:pk>/edit/', views.DailyLogUpdateView.as_view(), name='log_edit'),
    path('logs/<int:pk>/delete/', views.DailyLogDeleteView.as_view(), name='log_delete'),

    # Weekly Summary
    path('weekly/', views.WeeklySummaryListView.as_view(), name='weekly_list'),
    path('weekly/<int:week_number>/edit/', views.WeeklySummaryEditView.as_view(), name='weekly_edit'),

    # Reports
    path('report/', views.CompletionReportView.as_view(), name='completion_report'),

    # Exports & API
    path('export/csv/', views.export_logs_csv, name='export_csv'),
    path('api/logs/', views.api_logs, name='api_logs'),
]
