from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                  # 홈 화면
    path('signup/', views.signup_view, name='signup'), # 회원가입
    path('login/', views.login_view, name='login'),    # 로그인
    path('logout/', views.logout_view, name='logout'), # 로그아웃
    path('sentiment/', views.sentiment_view, name='sentiment'),  # 감정분석
    path('summarize/', views.summarize_view, name='summarize'),  # 텍스트 요약
    path('translate/', views.translate_view, name='translate'),  # 번역
]
