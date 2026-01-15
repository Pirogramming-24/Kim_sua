from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.http import HttpResponse
from .models import MovieReview, Movie
from .forms import MovieReviewForm
from .utils import fetch_tmdb_movies
from django.db.models import Q
from django.core.paginator import Paginator

# views.py 상단에 장르 맵 추가
TMDB_GENRE_MAP = {
    28: "액션", 12: "모험", 16: "애니메이션", 35: "코미디", 80: "범죄",
    99: "다큐멘터리", 18: "드라마", 10751: "가족", 14: "판타지", 36: "역사",
    27: "공포", 10402: "음악", 9648: "미스터리", 10749: "로맨스", 878: "SF",
    10770: "TV 영화", 53: "스릴러", 10752: "전쟁", 37: "서부"
}

def review_list(request):
    # 1. 파라미터 가져오기
    query = request.GET.get('q', '').strip() # 공백 제거
    search_type = request.GET.get('search_type', 'title')
    filter_type = request.GET.get('filter', 'all')
    sort_type = request.GET.get('sort', 'latest')

    # 데이터 자동 동기화
    if not Movie.objects.exists():
        fetch_tmdb_movies()

    # 2. 기본 쿼리셋 준비
    reviews_qs = MovieReview.objects.all()
    tmdb_qs = Movie.objects.all()

    # 3. [검색 로직] DB 필터링 수행
    if query:
        if search_type == 'title':
            reviews_qs = reviews_qs.filter(title__icontains=query)
            tmdb_qs = tmdb_qs.filter(title__icontains=query)
        elif search_type == 'director':
            reviews_qs = reviews_qs.filter(director__icontains=query)
            tmdb_qs = tmdb_qs.filter(director__icontains=query)
        elif search_type == 'actors':
            reviews_qs = reviews_qs.filter(actors__icontains=query)
            tmdb_qs = tmdb_qs.filter(actors__icontains=query)

    # 4. 필터링된 쿼리셋을 하나의 리스트로 통합
    combined_data = []

    # [내 리뷰 데이터 추가]
    if filter_type in ['all', 'my']:
        for r in reviews_qs: # 필터링된 reviews_qs 사용
            combined_data.append({
                'type': 'my',
                'pk': r.pk,
                'title': r.title,
                'year': r.year,
                'genre': r.genre,
                'rating': float(r.rating),
                'poster_url': r.poster.url if r.poster else None,
                'date': r.updated_at,
                'director': r.director,
                'actors': r.actors
            })

    # [TMDB 영화 데이터 추가]
    if filter_type in ['all', 'tmdb']:
        for m in tmdb_qs: # 필터링된 tmdb_qs 사용
            # 장르 이름 변환
            genre_display = TMDB_GENRE_MAP.get(int(m.genre_name), "기타") if m.genre_name.isdigit() else m.genre_name
            
            combined_data.append({
                'type': 'tmdb',
                'pk': m.tmdb_id,
                'title': m.title,
                'year': m.release_date.year if m.release_date else "미정",
                'genre': genre_display,
                'rating': m.vote_average / 2 if m.vote_average else 0,
                'poster_url': f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else None,
                'date': m.release_date,
                'director': m.director,
                'actors': m.actors
            })

    # 5. 정렬 수행
    if combined_data:
        if sort_type == 'latest':
            combined_data.sort(key=lambda x: str(x['date']) if x['date'] else '', reverse=True)
        elif sort_type == 'title':
            combined_data.sort(key=lambda x: x['title'])
        elif sort_type == 'rating':
            combined_data.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_type == 'year':
            combined_data.sort(key=lambda x: str(x['year']), reverse=True)

    # --- [추가: 페이지네이션 로직] ---
    page = request.GET.get('page', '1')
    paginator = Paginator(combined_data, 8)  # 한 페이지에 8개씩 노출
    page_obj = paginator.get_page(page)
    # ------------------------------

    context = {
        'reviews': page_obj,  # 기존 combined_data 대신 page_obj 전달
        'query': query,
        'search_type': search_type,
        'filter_type': filter_type,
        'sort_type': sort_type,
        'my_count': MovieReview.objects.count(),
        'tmdb_count': Movie.objects.count(),
        'total_count': len(combined_data),
    }
    return render(request, 'reviews/review_list.html', context)

def review_detail(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)
    review.runtime_display = review.runtime_in_hours()
    return render(request, 'reviews/review_detail.html', {'review': review})

def review_create(request):
    if request.method == 'POST':
        form = MovieReviewForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = MovieReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'create': True})

def review_update(request, pk):
    review = get_object_or_404(MovieReview, pk=pk)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = MovieReviewForm(instance=review)
    return render(request, 'reviews/review_form.html', {'form': form, 'create': False})

class MovieReviewDeleteView(DeleteView):
    model = MovieReview
    template_name = 'reviews/review_delete.html'
    success_url = reverse_lazy('review_list')

def update_movies(request):
    fetch_tmdb_movies()
    return redirect('review_list')