from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import MovieReview
from .forms import MovieReviewForm

# 리뷰 리스트
def review_list(request):
    reviews = MovieReview.objects.all().order_by('-updated_at')
    for review in reviews:
        review.runtime_display = review.runtime_in_hours()
    return render(request, 'reviews/review_list.html', {'reviews': reviews})

# 리뷰 디테일
def review_detail(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)
    review.runtime_display = review.runtime_in_hours()
    return render(request, 'reviews/review_detail.html', {'review': review})

# 리뷰 작성
from django.shortcuts import render, get_object_or_404, redirect
from .models import MovieReview
from .forms import MovieReviewForm

def review_create(request):
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('review_list')  # 저장 후 바로 리스트 페이지로 이동
    else:
        form = MovieReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'create': True})



# 리뷰 수정
def review_update(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_list')  # 수정 후에도 리스트로 이동
        else:
            print(form.errors)
    else:
        form = MovieReviewForm(instance=review)
    
    return render(request, 'reviews/review_form.html', {'form': form, 'create': False})

# 리뷰 삭제
class MovieReviewDeleteView(DeleteView):
    model = MovieReview
    template_name = 'reviews/review_delete.html'
    success_url = reverse_lazy('review_list')
