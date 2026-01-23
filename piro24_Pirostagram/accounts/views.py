from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .forms import SignUpForm, ProfileUpdateForm
from .models import User

# 회원가입
def signup(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다!')
            return redirect('posts:feed')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# 로그인
def user_login(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('posts:feed')
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'accounts/login.html')

# 로그아웃
@login_required
def user_logout(request):
    logout(request)
    return redirect('accounts:login')

# 프로필 보기
@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.post_set.all().order_by('-created_at')
    
    # 현재 로그인 사용자가 profile_user를 팔로우하고 있는지
    is_following = request.user in profile_user.followers.all()
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
    }
    return render(request, 'accounts/profile.html', context)

# 프로필 수정
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 업데이트되었습니다!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

# 팔로우/언팔로우 토글
@login_required
def follow_toggle(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)
    
    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        return JsonResponse({'error': '자기 자신은 팔로우할 수 없습니다.'}, status=400)
    
    if request.user in target_user.followers.all():
        # 이미 팔로우 중 → 언팔로우
        target_user.followers.remove(request.user)
        following = False
    else:
        # 팔로우
        target_user.followers.add(request.user)
        following = True
    
    return JsonResponse({
        'following': following,
        'followers_count': target_user.followers.count()
    })

# 유저 검색
@login_required
def user_search(request):
    query = request.GET.get('q', '')
    users = []
    
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:10]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        users_data = [{
            'id': user.id,
            'username': user.username,
            'profile_image': user.profile_image.url if user.profile_image else None,
        } for user in users]
        return JsonResponse({'users': users_data})
    
    return render(request, 'accounts/search.html', {'users': users, 'query': query})
