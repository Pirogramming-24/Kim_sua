from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Movie, MovieReview

admin.site.register(Movie)
admin.site.register(MovieReview)