from django.urls import path
from . import views

app_name='accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup' ),
    path('login/', views.login, name='login' ),
    path('logout/', views.logout, name='logout' ),
    path('delete/', views.delete, name='delete' ),
    path('update/', views.update, name='update' ),
    path('password/', views.change_password, name='change_password'),
    path('usersearch/', views.usersearch,name='usersearch'),
    path('<str:username>/', views.profile, name='profile'),
    path('<int:user_pk>/follow/', views.follow, name='follow'),
    path('<str:username>/recommendation/', views.recommendation, name='recommendation'),
    path('<int:pk>/review/', views.reviewIndex, name='reviewIndex'),
    path('<int:pk>/likemovieindex/', views.likeMovieIndex, name='likemovieindex'),
    path('<int:user_pk>/followerlist/', views.followerlist, name='followerlist'),
    path('<int:user_pk>/followinglist/', views.followinglist, name='followinglist'),


]
