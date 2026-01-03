from django.shortcuts import render, redirect, get_object_or_404
from .models import DevTool
from ideas.models import Idea

# 1. 목록 페이지
def devtool_list(request):
    return render(request, 'devtools/devtool_list.html', {
        'tools': DevTool.objects.all()
    })

# 2. 등록 페이지 (통합 폼 사용)
def devtool_create(request):
    if request.method == 'POST':
        # .get()을 사용하여 데이터 누락 시 KeyError 방지
        devtool = DevTool.objects.create(
            name=request.POST.get('name'),
            kind=request.POST.get('kind'),
            content=request.POST.get('content')
        )
        return redirect('devtools:devtool_detail', pk=devtool.id)
    
    # 등록 시에는 객체 없이 렌더링 (템플릿: DevTool Register 출력)
    return render(request, 'devtools/devtool_form.html')

# 3. 상세 페이지
def devtool_detail(request, pk):
    # 변수명을 devtool로 통일하여 일관성 유지
    devtool = get_object_or_404(DevTool, pk=pk)
    ideas = Idea.objects.filter(devtool=devtool)
    return render(request, 'devtools/devtool_detail.html', {
        'devtool': devtool,
        'ideas': ideas
    })

# 4. 수정 페이지 (통합 폼 사용)
def devtool_edit(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    
    if request.method == 'POST':
        devtool.name = request.POST.get('name')
        devtool.kind = request.POST.get('kind')
        devtool.content = request.POST.get('content')
        devtool.save()
        return redirect('devtools:devtool_detail', pk=devtool.id)
    
    # 수정 시에는 기존 객체 전달 (템플릿: DevTool Update 출력 및 값 채워짐)
    return render(request, 'devtools/devtool_form.html', {
        'devtool': devtool
    })

# 5. 삭제 로직
def devtool_delete(request, pk):
    if request.method == 'POST': 
        devtool = get_object_or_404(DevTool, pk=pk)
        devtool.delete()
    return redirect('devtools:devtool_list')