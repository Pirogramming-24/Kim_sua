from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Story(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author.username} - Story {self.id}'
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'stories'
        verbose_name_plural = 'Stories'

class StoryImage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stories/')
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f'Story {self.story.id} - Image {self.order}'
    
    class Meta:
        ordering = ['order']
        db_table = 'story_images'