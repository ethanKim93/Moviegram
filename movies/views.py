from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST, require_safe,require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Min, Max, Count, F, Sum
from django.db.models.functions import Round
import reviews
import math
from .models import Movie ,Video ,Image,Genre
from .forms import MovieForm
from reviews.models import Review
import requests
from reviews.views import movie_save
from accounts.sendemail import sendemail


# Create your views here.
IMAGE_LINK = 'https://image.tmdb.org/t/p/w500/'
@require_safe
def index(request):
    movies = Movie.objects.order_by('-pk')
    
    context = {
        'movies': movies,
    }
    return render(request, 'movies/index.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.user = request.user
            movie.save()
            return redirect('movies:detail', movie.pk)
    else:
        form = MovieForm()
    context = {
        'form': form,
    }
    return render(request, 'movies/create.html', context)

def detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    poster_path = IMAGE_LINK + movie.poster_path
    backdrop_path = IMAGE_LINK + movie.backdrop_path
    reviews = Review.objects.filter(movie=movie.pk)
    if reviews:
        movie_rank = round(reviews.aggregate(Avg('rank'))['rank__avg'],2)
    else:
        movie_rank = 0
    similar_movie_list = []
    similar_url = f'https://api.themoviedb.org/3/movie/{movie.tmdb_id}/similar?api_key={TMDB_API}&language=ko-KR&page=1'
    response = requests.get(similar_url)
    similar_movies = response.json()['results']
    for similar_movie in similar_movies[:10]:
        s_movie = Movie.objects.filter(tmdb_id=similar_movie['id'])
        if s_movie:
            try:
                similar_movie_list.append(get_object_or_404(Movie, tmdb_id=s_movie[0].tmdb_id))
            except:
                pass
            finally:
                continue
        similar_movie_id = similar_movie['id']
        detail_url = f'https://api.themoviedb.org/3/movie/{similar_movie_id}?api_key={TMDB_API}&language=ko-KR'
        response = requests.get(detail_url)
        s_movie = response.json()
        s_movie_pk = movie_save(s_movie)
        try:
            similar_movie_list.append(get_object_or_404(Movie, pk=s_movie_pk))
        except:
            pass
    movie_videos = Video.objects.filter(movie=movie)
    movie_imgs = Image.objects.filter(movie=movie)
    movie_genre = Genre.objects.filter(movies=movie)
    
    context = {
        'movie': movie,
        'poster_path':poster_path,
        'backdrop_path':backdrop_path,
        'reviews':reviews[:5],
        'reviews_all':reviews,
        'similar_movie_list':similar_movie_list,
        'movie_videos':movie_videos,
        'movie_imgs':movie_imgs,
        'movie_rank':movie_rank,
        'movie_genre':movie_genre
    }
    return render(request, 'movies/detail.html', context)


def likes(request, pk):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, pk=pk)
        if movie.movie_like.filter(pk=request.user.pk).exists():
            movie.movie_like.remove(request.user)
        else:
            # 좋아요 하기
            movie.movie_like.add(request.user)
        return redirect('movies:detail',movie.pk)
    return redirect('accounts:login')

def movie_reviews(request,pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = Review.objects.filter(movie=movie.pk)
    print(reviews)
    context = {
        'movie':movie,
        'reviews': reviews,
    }
    return render(request, 'movies/reviews.html', context)



