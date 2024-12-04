from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from .posts import PostsViews

from django.views import View
from django.db.models import Q

class SearchPostView(PostsViews, View):    
    def get(self, request):

        return render(request, 'search.html')
    
    def post(self, request):
        " Hàm tìm bài viết có tiêu đề, nội dung hoặc thể loại chứa ký tự tương ứng"
        search_box = request.POST.get('search_box', '')
        keys = Post.objects.filter(
            Q(content__icontains=search_box) |
            Q(category__icontains=search_box) |
            Q(title__icontains=search_box)
            ).select_related('admin')

        post_data = list(map(lambda post: {
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked_by_user': self.like_handler.user_liked_post(post.id),
            'post': post,
        }, keys))

        context = {
            'search_box': search_box,
            'posts': post_data,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        return render(request, 'search.html', context)
