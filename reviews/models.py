from django.db import models
from movies.models import Movie
from accounts.models import User
from django.conf import settings

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200,allow_unicode=True)

    def __str__(self):
        return f'{self.pk}: {self.name}'

    def get_absolute_url(self):
        return f'/reviews/tag/{self.slug}'
    
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE,related_name='review_movie')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='review_user')
    together = models.ManyToManyField(User,related_name='review_together',null=True,blank=True)
    review_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='review_like_user')
    title=models.CharField('',max_length=100)
    categoty_Choice = ((1,'★'),(2,'★★'),(3,'★★★'),(4,'★★★★'),(5,'★★★★★'),(6,'★★★★★★'),(7,'★★★★★★★'),(8,'★★★★★★★★'),(9,'★★★★★★★★★'),(10,'★★★★★★★★★★'))
    rank=models.FloatField('',choices=categoty_Choice)
    content=models.TextField('')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    place = models.TextField('',null=True,blank=True)
    picturepath=models.ImageField(blank=True, upload_to='reviews/', verbose_name="후기사진", null=True, )
    tags = models.ManyToManyField(Tag,blank=True)
    def __str__(self):
        return f'{self.pk}: {self.title}'

class Image(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,related_name='review_image')
    img_path = models.TextField()

    def __str__(self):
        return f'{self.pk}: {self.movie}'

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='comment_user')
    content = models.TextField('')
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return f'{self.pk}: {self.content}'


