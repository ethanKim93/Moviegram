
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import  AuthenticationForm
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth import login as auth_login 
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from movies.models import Movie
from reviews.models import Review
from .forms import CustomUserChangeForm, CustomUserCreationForm,CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from reviews.views import movie_save
from django.core.paginator import Paginator

import datetime
import random
import requests
from .models import User
from .sendemail import sendemail
from decouple import config

TMDB_API = config('TMDB_API')
KAKAO_API = config('KAKAO_API')
# Create your views here.
@require_http_methods(["GET","POST"])
def signup(request):
    if request.method=="POST":
        form=CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form=CustomUserCreationForm()
    context={
        'form':form,
    }
    return render(request, 'accounts/signup.html', context)

@require_http_methods(["GET","POST"])
def login(request):
    if request.user.is_authenticated:
        return redirect('reviews:index')

    if request.method=="POST":
        form=AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('reviews:index') 
    else:
        form=AuthenticationForm()
    context={
        'form':form,
    }
    return render(request, 'accounts/login.html', context)

@require_POST
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('reviews:index') 

@require_POST
def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        auth_logout(request)
    return redirect('reviews:index')

@login_required
@require_http_methods(["GET","POST"])
def update(request):
 
    if request.method=="POST":
        form=CustomUserChangeForm(request.POST,  request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('reviews:index')
    else:
        form=CustomUserChangeForm(instance=request.user)
    context={
        'form':form,
    }
    return render(request, 'accounts/update.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, '비밀번호가 변경 되었습니다.')
            return redirect('reviews:index')
        else:
            messages.error(request, '비밀번호 변경을 실패 하였습니다.')
    else:
        form = CustomPasswordChangeForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)
    
@login_required
def profile(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    reviews = Review.objects.filter(user=person.pk).order_by('-pk')[:4]
    movies = Movie.objects.filter(movie_like=person.pk).order_by('-pk')[:4]
    context = {
        'person': person,
        'reviews': reviews,
        'movies':movies
    }
    return render(request, 'accounts/profile.html', context)


# @require_POST
def follow(request, user_pk):
    # me=request.user
    # you=get_object_or_404(get_user_model(),pk=user_pk):
    if request.user.is_authenticated:
        person = get_object_or_404(get_user_model(), pk=user_pk)
        if person != request.user:
            #if request.user in person.followers.all():
            #내가 상대방의 팔로워 목록에 있다면
            #언팔로우
            if person.followers.filter(pk=request.user.pk).exists():
                person.followers.remove(request.user)
            else:
            #내가 상대방의 팔로워 목록에 없다면
            #팔로우
                person.followers.add(request.user)

                sendemail([request.user,person],'follow')
        return redirect('accounts:profile', person.username)
    return redirect('accounts:login') 



def recommendation(request, username):

    if request.user.is_authenticated:
        person = get_object_or_404(get_user_model(), username=username)
        
        followList =person.followings.all()
        recomendation_followers=Review.objects.filter(rank__gte=8, user__in=followList).prefetch_related('user')
        best_movie_list = []
        search_url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API}&language=ko-KR'
        response = requests.get(search_url)
        data = response.json()
        results = data['results']
        for result in results:
            best_movie = Movie.objects.filter(tmdb_id=result['id'])
            if best_movie:
                best_movie_list.append(get_object_or_404(Movie, tmdb_id=best_movie[0].tmdb_id))
                continue
            movie_id = result['id']
            detail_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API}&language=ko-KR'
            response = requests.get(detail_url)
            best_movie = response.json()
            best_movie_pk = movie_save(best_movie)
            best_movie_list.append(get_object_or_404(Movie, pk=best_movie_pk))
        now = datetime.datetime.now()
        nowYear = now.strftime('%Y')
        nowMonth = now.strftime('%m')
        remembers = Movie.objects.filter(release_date__icontains='-'+nowMonth+'-').distinct()
        year_list = {}
        for remember in remembers:
            re_year = remember.release_date[0:4]
            if re_year in year_list:
                year_list[re_year].append(remember)
            else:
                year_list[re_year] = [remember]
        random_key = random.choice(list(year_list.keys()))
        random_recommend = {
            'last_year':int(nowYear)-int(random_key),
            'movies':year_list[random_key],
            'month':nowMonth
            }
        context = {
            'best_movie_list':best_movie_list,
            'recomendation_followers': recomendation_followers,
            'remember':remember,
            'random_recommend':random_recommend
        }

        return render(request, 'accounts/recommendation.html', context)  
    return redirect('accounts:login') 




def reviewIndex(request,pk):
    reviews = Review.objects.filter(user=pk).order_by('-pk')
    paginator = Paginator(reviews, 12)
    person = get_object_or_404(get_user_model(), pk=pk)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reviews': page_obj,
        'person':person

    }
    return render(request, 'accounts/review_index.html', context)

def likeMovieIndex(request,pk):
    movie_like = Movie.objects.filter(movie_like=pk).order_by('-pk')
    person = get_object_or_404(get_user_model(), pk=pk)
    paginator = Paginator(movie_like, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'movie_like': page_obj,
        'person':person
    }
    return render(request, 'accounts/likeMovieIndex.html', context)

def usersearch(request): 
    search_key = request.GET['search_key'] 
    context = {'search_key':search_key} 
    return render(request,'accounts:usersearch.html',context)

def followerlist(request,user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk)
    followers = person.followers.all()
    context = {
        'person':person,
        'followers' : followers
    }
    return render(request, 'accounts/follower_list.html', context)
    
def followinglist(request,user_pk):
    person = get_object_or_404(get_user_model(), pk=user_pk)
    followings = person.followings.all()
    context = {
        'person':person,
        'followings' : followings
    }
    return render(request, 'accounts/following_list.html', context)
