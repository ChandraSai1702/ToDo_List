from django.urls import path
from . import views
from django_prometheus import exports

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/<int:pk>/update', views.task_update, name='task-update'),
    path('task/<int:pk>/delete/', views.task_delete, name='task-delete'),
    path('metrics/', views.metrics, name='metrics'),
]