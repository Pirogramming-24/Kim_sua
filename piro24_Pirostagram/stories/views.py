from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Story, StoryImage
from .forms import StoryForm

@login_required
def story_list(request):
    # 내가 팔로우한 사람들의 스토리 + 내 스토리
    following_users = request.user.following.all()
    cutoff_time = timezone.now() - timedelta(hours=24)
    
    stories = Story.objects.filter(
        author__in=following_users,
        created_at__gte=cutoff_time
    ) | Story.objects.filter(
        author=request.user,
        created_at__gte=cutoff_time
    )
    stories = stories.distinct().order_by('-created_at')
    
    return render(request, 'stories/story_list.html', {'stories': stories})

@login_required
def story_create(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')
        
        if not images:
            messages.error(request, '최소 1개 이상의 이미지를 업로드해주세요.')
            return render(request, 'stories/story_create.html', {'form': form})
        
        story = Story.objects.create(author=request.user)
        
        for idx, image in enumerate(images):
            StoryImage.objects.create(
                story=story,
                image=image,
                order=idx
            )
        
        messages.success(request, '스토리가 업로드되었습니다!')
        return redirect('stories:story_list')
    else:
        form = StoryForm()
    
    return render(request, 'stories/story_create.html', {'form': form})

@login_required
def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    
    # 스토리가 만료되었는지 확인
    if story.is_expired():
        messages.error(request, '이 스토리는 만료되었습니다.')
        return redirect('stories:story_list')
    
    # 팔로우한 사람의 스토리이거나 본인의 스토리만 볼 수 있음
    if story.author != request.user and not request.user.followers.filter(id=story.author.id).exists():
        messages.error(request, '이 스토리를 볼 권한이 없습니다.')
        return redirect('stories:story_list')
    
    images = story.images.all()
    
    return render(request, 'stories/story_detail.html', {'story': story, 'images': images})

@login_required
def story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    
    if story.author != request.user:
        messages.error(request, '스토리를 삭제할 권한이 없습니다.')
        return redirect('stories:story_list')
    
    if request.method == 'POST':
        story.delete()
        messages.success(request, '스토리가 삭제되었습니다!')
        return redirect('stories:story_list')
    
    return render(request, 'stories/story_delete.html', {'story': story})