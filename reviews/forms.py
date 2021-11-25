from django import forms
from django.forms import widgets
from .models import Review,Comment
from accounts.models import User
class ReviewForm(forms.ModelForm):
    #content = forms.CharField(widget=forms.Textarea(attrs={'class': 'editable text-left',
    #                                                       'style': 'height: auto;'}))#높}))#높이가 자동으로 따라감
    
    class Meta:

        model = Review
        exclude = ('movie','user','review_like',)
        widgets ={
            'title': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'제목을 입력하세요'
                }
            ),
            'together': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'함께 영화 본사람'

                }
            ),
            # 'content': forms.TextInput(
            #     attrs={
            #         #'class':'form-control',
            #         'class': 'editable text-left',
            #         'placeholder':'함께 영화 본사람',
            #         'style': 'height: auto;'
            #     }
            # ),  
            'content': forms.Textarea(
                attrs={
                    'class':'form-control',
                    'placeholder':'내용을 입력하세요'

                }
            ),
            'place': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'영화 본 장소'

                }
            ),
        }

class CommentForm(forms.ModelForm):
    # content = forms.CharField(),
    # widget=forms.Textarea(attrs={'class': 'editable text-left','placeholder': 'Enter a title',
    #                                                        'style': 'height: auto;'})


    class Meta:
        model = Comment
        # fields = '__all__'
        exclude = ('review', 'user')
        widgets ={
            'content': forms.TextInput(
                attrs={
                    'class':'form-control',
                    'placeholder':'후기에 대한 댓글을 입력해주세요!'
                }
            ),
        }