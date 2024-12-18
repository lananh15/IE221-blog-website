from django.shortcuts import render
from ..models import Post
from .posts import PostsViews

from django.views import View
from django.db.models import Q

class SearchPostView(PostsViews, View):    
    def get(self, request):
        """
        Hiển thị trang tìm kiếm bài viết
        Input:
            request (HttpRequest): Đối tượng yêu cầu từ user
        Output:
            HttpResponse: Trả về trang tìm kiếm (search.html) mà người dùng có thể nhập từ khóa để tìm kiếm bài viết
        """
        return render(request, 'search.html')
    
    def post(self, request):
        """
        Tìm kiếm bài viết theo tiêu đề, nội dung hoặc thể loại chứa từ khóa tìm kiếm
        Input:
            request (HttpRequest): Đối tượng yêu cầu từ client, chứa từ khóa tìm kiếm trong `search_box`
        Output:
            HttpResponse: Trả về trang tìm kiếm (search.html) với các bài viết phù hợp
        """
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
