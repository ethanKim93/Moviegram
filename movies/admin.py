from django.contrib import admin
from .models import Movie,Genre,Image,Video

# Register your models here.
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Image)
admin.site.register(Video)
