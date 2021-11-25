from django.urls import path
from . import views

app_name="movies"
urlpatterns = [
    path('index/', views.index,name='index'),
    path('<int:pk>/', views.detail,name='detail'),
    path('<int:pk>/likes/', views.likes, name='likes'),
    path('<int:pk>/movie_reviews/', views.movie_reviews,name='movie_reviews'),
    path('sendemail/', views.sendemail,name='sendemail'),


]
