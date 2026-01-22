from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.story_list, name='story_list'),
    path('create/', views.story_create, name='story_create'),
    path('<int:pk>/', views.story_detail, name='story_detail'),
    path('<int:pk>/delete/', views.story_delete, name='story_delete'),
]