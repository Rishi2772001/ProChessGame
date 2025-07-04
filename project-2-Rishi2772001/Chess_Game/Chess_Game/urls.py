"""
URL configuration for Chess_Game project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home, name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from Chess_app import views as chess_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('chess/', include('Chess_app.urls')),
    path('accounts/login/', chess_views.user_login, name='login'),
    path('accounts/logout/', chess_views.user_logout, name='logout'), 
    path('', chess_views.home),
    path('journal/', include('journal.urls')),
]
