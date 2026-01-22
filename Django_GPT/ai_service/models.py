from django.db import models
from django.contrib.auth.models import User

class ChatHistory(models.Model):
    MODEL_CHOICES = [
        ('sentiment', '감정 분석'),
        ('summarize', '텍스트 요약'),
        ('translate', '번역'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES)
    input_text = models.TextField()
    output_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.model_type} - {self.created_at}"