"""
URL configuration for bt2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('auth/', views.auth, name='auth'),
    path('accounts/', include('allauth.urls')),
    path('home/', views.home, name='home'),
    path('reserve/', views.reserve, name='reserve'),
    path('reserve_done/', views.reserve_done, name='reserve_done'),
    path('view_reservations/', views.view_reservations, name='view_reservations'),
    path('logout/', views.logout_view, name='logout'),
    path('delete/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),
    path('edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('edit_reservation_done/', views.edit_reservation_done, name='edit_reservation_done'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
