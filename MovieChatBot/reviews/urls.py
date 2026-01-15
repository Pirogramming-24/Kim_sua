from django.urls import path
from . import views
from chatbot.views import chatbot_view

urlpatterns = [
    path('', views.review_list, name='review_list'),  # FBV 사용
    path('create/', views.review_create, name='review_create'),
    path('<int:pk>/', views.review_detail, name='review_detail'),
    path('<int:pk>/update/', views.review_update, name='review_update'),
    path('<int:pk>/delete/', views.MovieReviewDeleteView.as_view(), name='review_delete'),
    path('update-movies/', views.update_movies, name='update_movies'),
    path('chatbot/', chatbot_view, name='chatbot'),
]
