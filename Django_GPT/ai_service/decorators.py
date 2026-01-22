from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

def login_required_with_alert(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "로그인 후 이용해주세요.")
            # LOGIN_URL 설정에 따라 로그인 페이지로 리다이렉트
            login_url = settings.LOGIN_URL
            # next 파라미터로 원래 요청한 URL 전달
            return redirect(f'{login_url}?next={request.path}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
