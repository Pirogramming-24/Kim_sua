from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Idea, IdeaStar
from devtools.models import DevTool

# 1. 목록 페이지
def idea_list(request):
    sort = request.GET.get('sort', 'latest')
    
    if sort == 'star':
        from django.db.models import F
        ideas_all = Idea.objects.annotate(
            starred=F('ideastar__is_starred')
        ).order_by('-starred', '-created_at')
    elif sort == 'name':
        ideas_all = Idea.objects.all().order_by('title')
    elif sort == 'registration':
        ideas_all = Idea.objects.all().order_by('created_at')
    else:  # latest
        ideas_all = Idea.objects.all().order_by('-created_at')

    paginator = Paginator(ideas_all, 4)
    page_number = request.GET.get('page')
    ideas = paginator.get_page(page_number)
    
    return render(request, 'ideas/idea_list.html', {'ideas': ideas, 'sort': sort})


# 2. 등록 페이지 (idea_form.html 사용)
def idea_create(request):
    if request.method == 'POST':
        # 새 아이디어 생성
        idea = Idea.objects.create(
            title=request.POST.get('title'),
            image=request.FILES.get('image'),  # 이미지가 없어도 에러나지 않음
            content=request.POST.get('content'),
            interest=request.POST.get('interest', 0),
            devtool_id=request.POST.get('devtool')
        )
        # 찜하기 데이터 초기화 생성
        IdeaStar.objects.create(idea=idea)
        return redirect('ideas:idea_detail', pk=idea.id)
    
    # 등록 시에는 빈 폼을 보여주기 위해 devtools만 전달
    return render(request, 'ideas/idea_form.html', {
        'devtools': DevTool.objects.all()
    })


# 3. 상세 페이지
def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    return render(request, 'ideas/idea_detail.html', {'idea': idea})


# 4. 수정 페이지 (idea_form.html 사용)
def idea_edit(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    
    if request.method == 'POST':
        # 기존 객체 값 업데이트
        idea.title = request.POST.get('title')
        idea.content = request.POST.get('content')
        idea.interest = request.POST.get('interest')
        idea.devtool_id = request.POST.get('devtool')
        
        # 새로운 이미지가 업로드된 경우에만 변경
        if 'image' in request.FILES:
            idea.image = request.FILES.get('image')
            
        idea.save()
        return redirect('ideas:idea_detail', pk=idea.id)
    
    # 수정 시에는 기존 'idea' 객체를 넘겨 폼에 값이 채워지게 함
    return render(request, 'ideas/idea_form.html', {
        'idea': idea, 
        'devtools': DevTool.objects.all()
    })


# 5. 삭제 기능
def idea_delete(request, pk):
    if request.method == 'POST':
        idea = get_object_or_404(Idea, pk=pk)
        idea.delete()
    return redirect('ideas:idea_list')


# 6. AJAX 찜하기
def idea_star(request, pk):
    star = get_object_or_404(IdeaStar, idea_id=pk)
    star.is_starred = not star.is_starred
    star.save()
    return JsonResponse({'is_starred': star.is_starred})


# 7. AJAX 관심도 조절
def idea_interest(request, pk):
    action = request.GET.get('action')
    idea = get_object_or_404(Idea, pk=pk)
    if action == 'plus':
        idea.interest += 1
    elif action == 'minus':
        idea.interest -= 1
    idea.save()
    return JsonResponse({'interest': idea.interest})