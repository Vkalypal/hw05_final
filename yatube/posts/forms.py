from django.utils.translation import gettext_lazy as _
from django import forms
from . models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст поста'),
        }
        help_texts = {
            'text': _('Введите текст поста'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            'text': _('Текст комментария'),
        }
        widgets = {'text': forms.Textarea(
            attrs={'placeholder': 'Оставьте комментарий...'}
        )}
