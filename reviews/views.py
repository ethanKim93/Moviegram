from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST, require_safe
from django.contrib.auth.decorators import login_required
from .models import Review, Comment,Tag
from movies.models import Movie,Genre, Video,Image
from .forms import ReviewForm,CommentForm
from movies.forms import MovieForm
from django.core.paginator import Paginator
from accounts.sendemail import sendemail
from django.utils.text import slugify
import requests
from django.db.models import Q
from decouple import config

TMDB_API = config('TMDB_API')
KAKAO_API = config('KAKAO_API')
# Create your views here.
def search(request):
    results = ''
    if request.user.is_authenticated:
        if request.method == 'POST':
            keyword= request.POST['keyword']
            search_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API}&language=ko-KR&query={keyword}&page=1&include_adult=false'
            response = requests.get(search_url)
            data = response.json()
            try:
                results = data['results']
            except:
                pass
        context = {
            'results' :results
        }
        return render(request, 'reviews/search.html', context)
    else:
        return redirect('accounts:login')
def create(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST, request.FILES,)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie_id = request.POST['movie_id']
                review.place = request.POST['movieplace']
                review.save()


                tags_str = request.POST['tags_str']
                if tags_str:
                    tags_str = tags_str.strip()
                    tags_str = tags_str.replace(',',';')
                    tags_list = tags_str.split(';')

                    for t in tags_list:
                        t = t.strip()
                        tag,is_tag_created = Tag.objects.get_or_create(name=t)
                        if is_tag_created:
                            tag.slug = slugify(t,allow_unicode=True)
                            tag.save()
                        review.tags.add(tag)
                
                mail_content ={
                    'user':review.user,
                    'review':review,
                }
                sendemail(mail_content,'newreview')
                if not request.POST['following_id'] == '함께 영화본 사람을 선택해주세요':
                    review.together.add(request.POST['following_id'])
                return redirect('reviews:detail',review.pk)
        else:
            movie_id = request.GET['movie_id']
            detail_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API}&language=ko-KR'
            response = requests.get(detail_url)
            movie = response.json()
            movie_pk = movie_save(movie)
            form = ReviewForm()
        context = {
            'form': form,
            'movie' :movie,
            'movie_pk' : movie_pk,
            'KAKAO_API':KAKAO_API

        }
        return render(request, 'reviews/create.html', context)
    else:
        return redirect('accounts:login')

def movie_save(movie):
    movie_id = movie['id']
    is_id = Movie.objects.filter(tmdb_id=movie_id)
    if not is_id:
        movie_save = Movie(title=movie['title'],overview=movie['overview'], release_date=movie['release_date'],
        poster_path=movie['poster_path'],tmdb_rank=movie['vote_average'],tmdb_id=int(movie['id']),runtime=movie['runtime'],backdrop_path=movie['backdrop_path'],tagline=movie['tagline'])
        movie_save.save() 
        for genre in movie['genres']:
                select_genre = Genre.objects.filter(genre_id=genre['id'])
                movie_save.genre.add(select_genre[0].pk)
        movie_video_url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API}&language=ko-KR'
        img_video_url = f'https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={TMDB_API}&language=ko'
        response_viedeo = requests.get(movie_video_url)
        response_img = requests.get(img_video_url)
        video_data = response_viedeo.json()
        img_data = response_img.json()

        movie_videos = video_data['results']
        movie_imgs = img_data['posters']
        for movie_video in movie_videos:
            movie_video_save = Video(movie=movie_save,youtube_key=movie_video['key'])
            movie_video_save.save()
        for movie_img in movie_imgs:
            movie_img_save = Image(movie=movie_save,file_path=movie_img['file_path'])
            movie_img_save.save()
        return movie_save.pk
    else:
        return is_id[0].pk

# @require_POST
def likes(request, pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=pk)
        if review.review_like.filter(pk=request.user.pk).exists():
            review.review_like.remove(request.user)
        else:
            # 좋아요 하기
            review.review_like.add(request.user)
            # mail_content ={
            #         'review':review,
            #         'like_user':request.user,
            #     }
            # sendemail(mail_content,'like')
        return redirect('reviews:detail',review.pk)
    return redirect('accounts:login')

def update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user == review.user:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('reviews:detail', review.pk)
        else:
            form = ReviewForm(instance=review)
    else:
        return redirect('reviews:index')
    context = {
        'review': review,
        'movie' :review.movie,
        'movie_pk' : review.movie.pk,
        'form': form,
        'KAKAO_API':KAKAO_API

    }
    return render(request, 'reviews/update.html', context)

def delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user.is_authenticated:
        if request.user == review.user: 
            review.delete()
            return redirect('reviews:index')
    return redirect('reviews:detail', review.pk)

def index(request):
    reviews = Review.objects.order_by('-pk')
    paginator = Paginator(reviews, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reviews': page_obj,
    }
    return render(request, 'reviews/index.html', context)


def detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    reviews = Review.objects.filter(movie=review.movie)
    comment_form = CommentForm()
    comments = review.review_comment.all()
    reviewTitle= Review.objects.filter(movie=review.movie).exclude(pk=review.pk)
    context = {
        'review': review,
        'comment_form': comment_form,
        'comments': comments,
        'reviewTitle':reviewTitle,
    }
    return render(request, 'reviews/detail.html', context)

@require_POST
def comments_create(request, pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=pk)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
            mail_content ={
                    'review':review,
                    'comment':comment,
                }
            sendemail(mail_content,'comment')
        return redirect('reviews:detail', review.pk)
    return redirect('accounts:login')


@require_POST
def comments_delete(request, review_pk, comment_pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
    return redirect('reviews:detail', review_pk)

def tag_page(request,slug):
    tag = Tag.objects.get(slug=slug)
    reviews = tag.review_set.all()
    paginator = Paginator(reviews, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reviews' :page_obj,
        'tag':tag,
    }
    return render(request, 'reviews/tagdetail.html', context)

def reviewsearch(request):
    if request.method == 'POST':
        keyword= request.POST['reviewkeyword']
        review_list = Review.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(tags__name__icontains=keyword)
        ).distinct()

        paginator = Paginator(review_list, 12)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'reviews': page_obj,
            'keyword': keyword
        }
        return render(request, 'reviews/index.html', context)
    else:
        return redirect('reviews:index')