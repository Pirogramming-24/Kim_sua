"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
# --- [미디어 파일 설정을 위해 추가] ---
from django.conf import settings
from django.conf.urls.static import static
# ----------------------------------

urlpatterns = [
    path('admin/', admin.site.urls), # 어드민 페이지 (있으면 좋음)
    path('', include('reviews.urls')),
]

# --- [개발 환경에서 미디어 파일(이미지)을 서빙하기 위한 설정] ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ---------------------------------------------------------