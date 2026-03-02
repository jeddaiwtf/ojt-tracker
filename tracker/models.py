"""
OJT Tracker - Models
Relationships:
  User (built-in) ──1:1──► UserProfile
  UserProfile ──1:N──► DailyLog
  UserProfile ──1:N──► WeeklySummary
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import math


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=150)
    supervisor = models.CharField(max_length=150)
    total_required_hours = models.DecimalField(
        max_digits=6, decimal_places=2, default=448,
        help_text="Total OJT hours required (default 448)"
    )
    ojt_start_date = models.DateField(help_text="Official OJT start date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.department}"

    @property
    def total_hours_rendered(self):
        """Sum of all approved daily log hours."""
        result = self.daily_logs.aggregate(total=models.Sum('daily_hours'))
        return result['total'] or 0

    @property
    def remaining_hours(self):
        remaining = float(self.total_required_hours) - float(self.total_hours_rendered)
        return max(remaining, 0)

    @property
    def completion_percentage(self):
        if float(self.total_required_hours) == 0:
            return 0
        pct = (float(self.total_hours_rendered) / float(self.total_required_hours)) * 100
        return min(round(pct, 2), 100)

    @property
    def is_complete(self):
        return float(self.total_hours_rendered) >= float(self.total_required_hours)


class DailyLog(models.Model):
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='daily_logs'
    )
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField()
    daily_hours = models.DecimalField(
        max_digits=5, decimal_places=2, editable=False,
        help_text="Auto-calculated: (time_out - time_in) - 1hr lunch"
    )
    week_number = models.PositiveIntegerField(
        editable=False,
        help_text="Custom week number based on OJT start date"
    )
    remarks = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        unique_together = [('profile', 'date')]   # Prevent duplicate date entries
        verbose_name = 'Daily Log'
        verbose_name_plural = 'Daily Logs'

    def __str__(self):
        return f"{self.profile.user.username} | {self.date} | {self.daily_hours}h"

    # ── Business logic ────────────────────────────────────────────────────────
    def compute_daily_hours(self):
        """(time_out - time_in) - 1 hour lunch break. Returns Decimal."""
        from datetime import datetime, date
        dt_in = datetime.combine(date.today(), self.time_in)
        dt_out = datetime.combine(date.today(), self.time_out)
        diff_seconds = (dt_out - dt_in).total_seconds()
        hours = (diff_seconds / 3600) - 1  # subtract 1-hr lunch
        return round(max(hours, 0), 2)

    def compute_week_number(self):
        """Week 1 = days 0-6 from start date. Formula: floor((date - start) / 7) + 1"""
        delta = (self.date - self.profile.ojt_start_date).days
        return math.floor(delta / 7) + 1

    def clean(self):
        errors = {}

        # Time Out must be after Time In
        if self.time_in and self.time_out:
            if self.time_out <= self.time_in:
                errors['time_out'] = "Time Out must be later than Time In."

        # Cannot log before OJT start date
        if self.date and self.profile_id:
            try:
                profile = self.profile
                if self.date < profile.ojt_start_date:
                    errors['date'] = (
                        f"Cannot log before your OJT start date ({profile.ojt_start_date})."
                    )
            except UserProfile.DoesNotExist:
                pass

        if errors:
            raise ValidationError(errors)

        # Compute derived fields after validation
        computed = self.compute_daily_hours()
        if computed > 24:
            raise ValidationError({'time_out': "Daily hours cannot exceed 24 hours."})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.daily_hours = self.compute_daily_hours()
        self.week_number = self.compute_week_number()
        super().save(*args, **kwargs)


class WeeklySummary(models.Model):
    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='weekly_summaries'
    )
    week_number = models.PositiveIntegerField()
    weekly_learnings = models.TextField(blank=True, default='')
    major_tasks = models.TextField(blank=True, default='', verbose_name='Major Tasks Completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['week_number']
        unique_together = [('profile', 'week_number')]
        verbose_name = 'Weekly Summary'
        verbose_name_plural = 'Weekly Summaries'

    def __str__(self):
        return f"{self.profile.user.username} | Week {self.week_number}"

    @property
    def total_hours(self):
        result = self.profile.daily_logs.filter(week_number=self.week_number).aggregate(
            total=models.Sum('daily_hours')
        )
        return result['total'] or 0

    @property
    def log_dates(self):
        return self.profile.daily_logs.filter(
            week_number=self.week_number
        ).values_list('date', flat=True)
