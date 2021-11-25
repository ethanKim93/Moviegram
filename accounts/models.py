from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.base import Model


# Create your models here.
class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')  
    nickname=models.CharField(max_length=30, verbose_name="닉네임")
    introduce=models.CharField(max_length=100, verbose_name="인사말")
    posterpath=models.ImageField(blank=True, upload_to='profiles/', verbose_name="프로필사진", null=True, )

    
    # def __str__(self):
    #     return self.nickname


