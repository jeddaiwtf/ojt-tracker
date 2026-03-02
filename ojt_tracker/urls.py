from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout

def logout_view(request):
    auth_logout(request)
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('tracker.urls')),
]