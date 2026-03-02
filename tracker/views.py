"""
OJT Tracker - Views (Class-Based Views preferred)
"""

import json
import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView
)

from .forms import DailyLogForm, UserProfileForm, UserRegistrationForm, WeeklySummaryForm
from .models import DailyLog, UserProfile, WeeklySummary


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_profile_or_redirect(user):
    """Returns (profile, redirect_response). One will be None."""
    try:
        return user.profile, None
    except UserProfile.DoesNotExist:
        return None, redirect('profile_create')


# ─── Auth / Registration ──────────────────────────────────────────────────────

class RegisterView(View):
    template_name = 'tracker/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            messages.success(request, "Account created! Complete your OJT profile.")
            return redirect('profile_create')
        return render(request, self.template_name, {'form': form})


# ─── User Profile ─────────────────────────────────────────────────────────────

class ProfileCreateView(LoginRequiredMixin, View):
    template_name = 'tracker/profile_form.html'

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            return redirect('profile_edit')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = UserProfileForm()
        return render(request, self.template_name, {'form': form, 'title': 'Create OJT Profile'})

    def post(self, request):
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile created successfully!")
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form, 'title': 'Create OJT Profile'})


class ProfileEditView(LoginRequiredMixin, View):
    template_name = 'tracker/profile_form.html'

    def get(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir
        form = UserProfileForm(instance=profile)
        return render(request, self.template_name, {'form': form, 'title': 'Edit OJT Profile'})

    def post(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form, 'title': 'Edit OJT Profile'})


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, View):
    template_name = 'tracker/dashboard.html'

    def get(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir

        # Weekly hours aggregation for Chart.js
        weekly_data = (
            profile.daily_logs
            .values('week_number')
            .annotate(total=Sum('daily_hours'))
            .order_by('week_number')
        )
        chart_labels = [f"Week {w['week_number']}" for w in weekly_data]
        chart_data = [float(w['total']) for w in weekly_data]

        # Recent logs (last 7 entries)
        recent_logs = profile.daily_logs.order_by('-date')[:7]

        context = {
            'profile': profile,
            'total_required': float(profile.total_required_hours),
            'total_rendered': float(profile.total_hours_rendered),
            'remaining': float(profile.remaining_hours),
            'completion_pct': profile.completion_percentage,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'recent_logs': recent_logs,
        }
        return render(request, self.template_name, context)


# ─── Daily Logs ───────────────────────────────────────────────────────────────

class DailyLogListView(LoginRequiredMixin, View):
    template_name = 'tracker/log_list.html'

    def get(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir
        logs = profile.daily_logs.order_by('-date')
        return render(request, self.template_name, {'logs': logs, 'profile': profile})


class DailyLogCreateView(LoginRequiredMixin, View):
    template_name = 'tracker/log_form.html'

    def get(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir
        form = DailyLogForm(profile=profile, initial={'date': date.today()})
        return render(request, self.template_name, {'form': form, 'title': 'Add Daily Log'})

    def post(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir
        form = DailyLogForm(request.POST, profile=profile)
        if form.is_valid():
            log = form.save(commit=False)
            log.profile = profile
            try:
                log.save()
                messages.success(request, f"Log for {log.date} saved. Hours: {log.daily_hours}h")
                return redirect('log_list')
            except Exception as e:
                messages.error(request, str(e))
        return render(request, self.template_name, {'form': form, 'title': 'Add Daily Log'})


class DailyLogUpdateView(LoginRequiredMixin, View):
    template_name = 'tracker/log_form.html'

    def _get_log(self, request, pk):
        return get_object_or_404(DailyLog, pk=pk, profile__user=request.user)

    def get(self, request, pk):
        log = self._get_log(request, pk)
        form = DailyLogForm(instance=log, profile=log.profile)
        return render(request, self.template_name, {'form': form, 'title': 'Edit Daily Log', 'log': log})

    def post(self, request, pk):
        log = self._get_log(request, pk)
        form = DailyLogForm(request.POST, instance=log, profile=log.profile)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Log updated successfully.")
                return redirect('log_list')
            except Exception as e:
                messages.error(request, str(e))
        return render(request, self.template_name, {'form': form, 'title': 'Edit Daily Log', 'log': log})


class DailyLogDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        log = get_object_or_404(DailyLog, pk=pk, profile__user=request.user)
        log.delete()
        messages.success(request, "Log deleted.")
        return redirect('log_list')


# ─── Weekly Summary ───────────────────────────────────────────────────────────

class WeeklySummaryListView(LoginRequiredMixin, View):
    template_name = 'tracker/weekly_list.html'

    def get(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir

        # Build week data: distinct weeks from daily logs
        weeks_qs = (
            profile.daily_logs
            .values('week_number')
            .annotate(total_hours=Sum('daily_hours'))
            .order_by('week_number')
        )

        weeks = []
        for w in weeks_qs:
            wnum = w['week_number']
            summary, _ = WeeklySummary.objects.get_or_create(
                profile=profile, week_number=wnum
            )
            weeks.append({
                'week_number': wnum,
                'total_hours': float(w['total_hours']),
                'summary': summary,
            })

        return render(request, self.template_name, {'weeks': weeks, 'profile': profile})


class WeeklySummaryEditView(LoginRequiredMixin, View):
    template_name = 'tracker/weekly_form.html'

    def _get_summary(self, request, week_number):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return None, None, redir
        summary, _ = WeeklySummary.objects.get_or_create(
            profile=profile, week_number=week_number
        )
        return profile, summary, None

    def get(self, request, week_number):
        profile, summary, redir = self._get_summary(request, week_number)
        if redir:
            return redir
        form = WeeklySummaryForm(instance=summary)
        logs = profile.daily_logs.filter(week_number=week_number).order_by('date')
        return render(request, self.template_name, {
            'form': form, 'summary': summary, 'logs': logs,
            'week_number': week_number,
            'total_hours': sum(float(l.daily_hours) for l in logs),
        })

    def post(self, request, week_number):
        profile, summary, redir = self._get_summary(request, week_number)
        if redir:
            return redir
        form = WeeklySummaryForm(request.POST, instance=summary)
        if form.is_valid():
            form.save()
            messages.success(request, f"Week {week_number} notes saved.")
            return redirect('weekly_list')
        logs = profile.daily_logs.filter(week_number=week_number).order_by('date')
        return render(request, self.template_name, {
            'form': form, 'summary': summary, 'logs': logs,
            'week_number': week_number,
            'total_hours': sum(float(l.daily_hours) for l in logs),
        })


# ─── Completion Report ────────────────────────────────────────────────────────

class CompletionReportView(LoginRequiredMixin, View):
    template_name = 'tracker/completion_report.html'

    def get(self, request):
        profile, redir = get_profile_or_redirect(request.user)
        if redir:
            return redir

        weekly_summaries = WeeklySummary.objects.filter(profile=profile).order_by('week_number')
        all_logs = profile.daily_logs.order_by('date')

        # Aggregate weekly data for report table
        weekly_hours = (
            profile.daily_logs
            .values('week_number')
            .annotate(total=Sum('daily_hours'))
            .order_by('week_number')
        )

        context = {
            'profile': profile,
            'user': request.user,
            'weekly_summaries': weekly_summaries,
            'weekly_hours': weekly_hours,
            'all_logs': all_logs,
            'total_required': float(profile.total_required_hours),
            'total_rendered': float(profile.total_hours_rendered),
            'remaining': float(profile.remaining_hours),
            'completion_pct': profile.completion_percentage,
            'today': date.today(),
        }
        return render(request, self.template_name, context)


# ─── CSV Export ───────────────────────────────────────────────────────────────

@login_required
def export_logs_csv(request):
    profile, redir = get_profile_or_redirect(request.user)
    if redir:
        return redir

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ojt_logs_{request.user.username}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Week #', 'Time In', 'Time Out', 'Daily Hours', 'Remarks'])
    for log in profile.daily_logs.order_by('date'):
        writer.writerow([
            log.date, log.week_number,
            log.time_in.strftime('%H:%M'), log.time_out.strftime('%H:%M'),
            log.daily_hours, log.remarks
        ])
    return response


# ─── REST API (basic) ─────────────────────────────────────────────────────────

@login_required
def api_logs(request):
    profile, redir = get_profile_or_redirect(request.user)
    if redir:
        return JsonResponse({'error': 'Profile not found'}, status=404)

    logs = list(profile.daily_logs.order_by('date').values(
        'id', 'date', 'time_in', 'time_out', 'daily_hours', 'week_number', 'remarks'
    ))
    # Convert time/date to strings for JSON
    for log in logs:
        log['date'] = str(log['date'])
        log['time_in'] = str(log['time_in'])
        log['time_out'] = str(log['time_out'])
        log['daily_hours'] = str(log['daily_hours'])

    return JsonResponse({
        'profile': {
            'name': request.user.get_full_name(),
            'department': profile.department,
            'total_required': str(profile.total_required_hours),
            'total_rendered': str(profile.total_hours_rendered),
            'completion_pct': profile.completion_percentage,
        },
        'logs': logs,
    })
