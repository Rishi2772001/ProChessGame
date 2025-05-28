# Chess_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
    path('history/', views.history, name='history'),
    path('join/', views.join, name='join'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('guest_access/', views.guest_access, name='guest_access'),
    path('no_game/', views.no_game, name='no_game'),
    path('invite-player/', views.send_invite, name='send_invite'),
    path('accept-invite/<int:invite_id>/', views.accept_invite, name='accept_invite'),
    path('invites/', views.view_invites, name='view_invites'),
    path('decline-invite/<int:invite_id>/', views.decline_invite, name='decline_invite'),
    path('delete_game/<int:game_id>/', views.delete_game, name='delete_game'),
    # Removed URLs related to AJAX polling
]
