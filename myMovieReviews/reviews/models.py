from django.db import models

class MovieReview(models.Model):
    GENRE_CHOICES = [
        ('액션', '액션'),
        ('로맨스', '로맨스'),
        ('코미디', '코미디'),
        ('드라마', '드라마'),
        ('멜로', '멜로'),
        ('SF', 'SF'),
        ('공포', '공포'),
        ('스포츠', '스포츠'),
        ('뮤지컬', '뮤지컬'),
        ('기타', '기타'),
    ]

    title = models.CharField(max_length=100)
    year = models.IntegerField()
    director = models.CharField(max_length=50)
    actors = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    runtime = models.IntegerField(help_text="분 단위로 입력")
    content = models.TextField()

    # updated_at만 남기기
    updated_at = models.DateTimeField(auto_now=True)

    def runtime_in_hours(self):
        hours = self.runtime // 60
        minutes = self.runtime % 60
        return f"{hours}시간 {minutes}분" if hours else f"{minutes}분"

    def __str__(self):
        return self.title
