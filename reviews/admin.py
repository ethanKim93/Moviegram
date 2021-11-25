from django.contrib import admin
from .models import Review,Image,Comment,Tag

# Register your models here.
admin.site.register(Review)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Tag)
