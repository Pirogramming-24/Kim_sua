import traceback
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Post
from .forms import PostForm

# services 폴더에서 로직 불러오기
from .services.ocr_service import extract_nutrition_text
from .services.hashtag_service import generate_hashtags

# 1. 메인 목록 페이지 (검색 및 가격 필터 포함)
def main(request):
    posts = Post.objects.all().order_by('-id')
    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'posts/list.html', context=context)

# 2. 게시글 생성 페이지
def create(request):
    if request.method == 'GET':
        form = PostForm()
        context = { 'form': form }
        return render(request, 'posts/create.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            # 이미지가 있을 경우 해시태그 자동 생성 (필요 시 주석 해제)
            # if post.photo:
            #     tags = generate_hashtags(post.photo)
            post.save()
            return redirect('/')
        return render(request, 'posts/create.html', {'form': form})

# 3. 게시글 상세 페이지
def detail(request, pk):
    target_post = Post.objects.get(id=pk)

    form = PostForm(instance=target_post)
    
    context = { 
        'post': target_post,
        'form': form, 
    }
    return render(request, 'posts/detail.html', context=context)

# 4. 게시글 수정 페이지
def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = { 'form': form, 'post': post }
        return render(request, 'posts/update.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:detail', pk=pk)
        return render(request, 'posts/update.html', {'form': form, 'post': post})

# 5. 게시글 삭제
def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

# 6. [핵심] 비동기 OCR 분석 뷰
# 프론트엔드 JS에서 /analyze-ocr/ 경로로 이미지를 보낼 때 응답함
def analyze_ocr(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        try:
            print("--- [DEBUG] OCR 단계 시작 ---")
            # ocr_service.py의 extract_nutrition_text 호출
            # 반환값 예: {'calories': 390.0, 'carbs': 60.0, 'protein': 3.8, 'fat': 15.0}
            nutrition_data = extract_nutrition_text(image)
            
            print(f"--- [DEBUG] 최종 추출 데이터: {nutrition_data} ---")
            
            # 클라이언트(JS)에 파싱된 결과 전달
            return JsonResponse(nutrition_data)
            
        except Exception as e:
            print("\n!!! [OCR VIEW ERROR] !!!")
            traceback.print_exc() 
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)