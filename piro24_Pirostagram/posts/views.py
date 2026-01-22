from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment
from .forms import PostForm, CommentForm

@login_required
def feed(request):
    # 내가 팔로우한 사람들의 게시글 + 내 게시글
    following_users = request.user.following.all()
    posts = Post.objects.filter(
        author__in=following_users
    ) | Post.objects.filter(author=request.user)
    posts = posts.distinct().order_by('-created_at')
    
    return render(request, 'posts/feed.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다!')
            return redirect('posts:feed')
    else:
        form = PostForm()
    
    return render(request, 'posts/post_create.html', {'form': form})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, '게시글을 수정할 권한이 없습니다.')
        return redirect('posts:post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 수정되었습니다!')
            return redirect('posts:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'posts/post_edit.html', {'form': form, 'post': post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author != request.user:
        messages.error(request, '게시글을 삭제할 권한이 없습니다.')
        return redirect('posts:post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '게시글이 삭제되었습니다!')
        return redirect('posts:feed')
    
    return render(request, 'posts/post_delete.html', {'post': post})

@login_required
def like_toggle(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)
    
    post = get_object_or_404(Post, pk=pk)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })

@login_required
def comment_create(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)
    
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': '댓글 내용을 입력해주세요.'}, status=400)
    
    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content
    )
    
    return JsonResponse({
        'id': comment.id,
        'content': comment.content,
        'author': comment.author.username,
        'author_profile': comment.author.profile_image.url if comment.author.profile_image else None,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        'can_edit': True
    })

@login_required
def comment_edit(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)
    
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.author != request.user:
        return JsonResponse({'error': '댓글을 수정할 권한이 없습니다.'}, status=403)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': '댓글 내용을 입력해주세요.'}, status=400)
    
    comment.content = content
    comment.save()
    
    return JsonResponse({
        'id': comment.id,
        'content': comment.content,
        'updated_at': comment.updated_at.strftime('%Y-%m-%d %H:%M')
    })

@login_required
def comment_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)
    
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.author != request.user:
        return JsonResponse({'error': '댓글을 삭제할 권한이 없습니다.'}, status=403)
    
    comment.delete()
    
    return JsonResponse({'success': True})

@login_required
def feed(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(author__in=list(following_users) + [request.user]).order_by('-created_at')

    return render(request, 'posts/feed.html', {'posts': posts})
