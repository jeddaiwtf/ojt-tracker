"""
OJT Tracker - Forms
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from .models import UserProfile, DailyLog, WeeklySummary


# ─── Registration / Profile ───────────────────────────────────────────────────

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name', css_class='col-md-6'), Column('last_name', css_class='col-md-6')),
            'username', 'email',
            Row(Column('password1', css_class='col-md-6'), Column('password2', css_class='col-md-6')),
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department', 'supervisor', 'total_required_hours', 'ojt_start_date']
        widgets = {
            'ojt_start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('department', css_class='col-md-6'), Column('supervisor', css_class='col-md-6')),
            Row(
                Column('total_required_hours', css_class='col-md-6'),
                Column('ojt_start_date', css_class='col-md-6'),
            ),
            Submit('submit', 'Save Profile', css_class='btn btn-primary px-4'),
        )


# ─── Daily Log ────────────────────────────────────────────────────────────────

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ['date', 'time_in', 'time_out', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_in': forms.TimeInput(attrs={'type': 'time'}),
            'time_out': forms.TimeInput(attrs={'type': 'time'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'date',
            Row(Column('time_in', css_class='col-md-6'), Column('time_out', css_class='col-md-6')),
            'remarks',
            Submit('submit', 'Save Log', css_class='btn btn-primary px-4 mt-2'),
        )

    def clean(self):
        cleaned_data = super().clean()
        time_in = cleaned_data.get('time_in')
        time_out = cleaned_data.get('time_out')
        date = cleaned_data.get('date')

        if time_in and time_out:
            if time_out <= time_in:
                raise forms.ValidationError("Time Out must be later than Time In.")

        if date and self.profile:
            if date < self.profile.ojt_start_date:
                raise forms.ValidationError(
                    f"Cannot log before OJT start date ({self.profile.ojt_start_date})."
                )

        return cleaned_data


# ─── Weekly Summary ───────────────────────────────────────────────────────────

class WeeklySummaryForm(forms.ModelForm):
    class Meta:
        model = WeeklySummary
        fields = ['weekly_learnings', 'major_tasks']
        widgets = {
            'weekly_learnings': forms.Textarea(attrs={'rows': 5, 'placeholder': 'What did you learn this week?'}),
            'major_tasks': forms.Textarea(attrs={'rows': 5, 'placeholder': 'List major tasks you completed...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'weekly_learnings',
            'major_tasks',
            Submit('submit', 'Save Notes', css_class='btn btn-primary px-4 mt-2'),
        )
