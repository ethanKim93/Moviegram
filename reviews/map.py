
from django.shortcuts import render, redirect, get_object_or_404

def kakao(request):
    return render(request, 'reviews/kakaomap.html')
