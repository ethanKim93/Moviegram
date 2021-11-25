from django.db import models
from django.conf import settings

# Create your models here.
class Genre(models.Model):
    genre_name = models.TextField()
    genre_id=models.IntegerField()

    def __str__(self):
        return f'{self.genre_id}: {self.genre_name}'

class Movie(models.Model):

    genre=models.ManyToManyField(Genre, related_name='movies',null=True,blank=True)
    movie_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='movie_like_user')
    title=models.CharField(max_length=100)
    overview=models.TextField()
    release_date=models.TextField()
    user_rank=models.FloatField(null=True,blank=True)
    poster_path=models.TextField()
    tmdb_rank=models.TextField()
    tmdb_id=models.TextField()
    runtime=models.TextField()
    backdrop_path=models.TextField(null=True,blank=True)
    tagline=models.TextField() #영화 명대사

    def __str__(self):
        return f'{self.pk}: {self.title}'

class Image(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    file_path = models.TextField()

    def __str__(self):
        return f'{self.pk}: {self.movie}'

class Video(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    youtube_key = models.TextField()

    def __str__(self):
        return f'{self.pk}: {self.movie}'