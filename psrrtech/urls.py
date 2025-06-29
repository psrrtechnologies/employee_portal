from django.urls import path
from .views import dashboard_router

urlpatterns = [
    path('dashboard/', dashboard_router, name='dashboard'),
]
