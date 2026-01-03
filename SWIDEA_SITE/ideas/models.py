from django.db import models
from devtools.models import DevTool

class Idea(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ideas/%Y/%m/%d/')
    content = models.TextField()
    interest = models.IntegerField(default=0)
    devtool = models.ForeignKey(DevTool, on_delete=models.CASCADE, related_name='ideas')
    created_at = models.DateTimeField(auto_now_add=True)

class IdeaStar(models.Model):
    idea = models.OneToOneField(Idea, on_delete=models.CASCADE, related_name='ideastar')
    is_starred = models.BooleanField(default=False)