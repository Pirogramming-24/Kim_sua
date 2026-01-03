from django.urls import path
from . import views

app_name = 'ideas'

urlpatterns = [
    path('', views.idea_list, name='idea_list'),
    path('create/', views.idea_create, name='idea_create'),
    path('<int:pk>/', views.idea_detail, name='idea_detail'),
    path('<int:pk>/edit/', views.idea_edit, name='idea_edit'),
    path('<int:pk>/delete/', views.idea_delete, name='idea_delete'),
    path('<int:pk>/star/', views.idea_star, name='idea_star'),
    path('<int:pk>/interest/', views.idea_interest, name='idea_interest'),
]