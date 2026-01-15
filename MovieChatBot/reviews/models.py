from django.db import models

# [수정] TMDB 영화 정보를 저장할 모델 (감독, 배우 필드 추가)
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # TMDB 고유 ID (중복 저장 방지용)
    title = models.CharField(max_length=200)
    overview = models.TextField(blank=True)     # 줄거리 (AI 챗봇의 핵심 재료)
    release_date = models.DateField(null=True, blank=True)
    poster_path = models.CharField(max_length=500, null=True, blank=True) # 포스터 경로
    vote_average = models.FloatField(default=0) # TMDB 평점
    poster = models.ImageField(upload_to='posters/', null=True, blank=True) # 로컬 포스터 저장용
    genre_name = models.CharField(max_length=100, default="기타")
    
    # --- [추가 부분] ---
    director = models.CharField(max_length=100, null=True, blank=True) # 감독 정보
    actors = models.TextField(null=True, blank=True)                  # 배우 정보 (여러 명일 수 있어 TextField)
    # ------------------

    def __str__(self):
        return self.title

# [수정] 기존 리뷰 모델
class MovieReview(models.Model):
    GENRE_CHOICES = [
        ('액션', '액션'), ('로맨스', '로맨스'), ('코미디', '코미디'),
        ('드라마', '드라마'), ('멜로', '멜로'), ('SF', 'SF'),
        ('공포', '공포'), ('스포츠', '스포츠'), ('뮤지컬', '뮤지컬'), ('기타', '기타'),
    ]

    # 실제 영화 정보와 연결 (선택 사항)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    title = models.CharField(max_length=100)
    year = models.IntegerField()
    director = models.CharField(max_length=50)
    actors = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    runtime = models.IntegerField(help_text="분 단위로 입력")
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)

    def runtime_in_hours(self):
        hours = self.runtime // 60
        minutes = self.runtime % 60
        return f"{hours}시간 {minutes}분" if hours else f"{minutes}분"

    def __str__(self):
        return f"{self.title} - {self.rating}점"