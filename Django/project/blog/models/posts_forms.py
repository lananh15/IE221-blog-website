from tinymce.widgets import TinyMCE
from django import forms
from .posts import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'title', 'content', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'box', 'placeholder': 'Enter your name'}),
            'title': forms.TextInput(attrs={'class': 'box', 'placeholder': 'Add post title'}),
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),  # Sử dụng TinyMCE cho content
            'category': forms.Select(attrs={'class': 'box'}),
            'image': forms.FileInput(attrs={'class': 'box'}),
        }
