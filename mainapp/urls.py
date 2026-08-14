from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('report/', views.report, name='report'),
    path('report/download/', views.report_download, name='report_download') 
]