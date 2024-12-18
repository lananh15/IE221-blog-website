from django.shortcuts import render, redirect
from ..models import Post, Comment

from .base import BaseView
from .comments import CommentViews
from .likes import LikeViews
from .users import UserViews

class PostsViews(BaseView):
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.session.get('user_id', None)
        self.admin_id = request.session.get('admin_id', None)
        self.initialize_handlers()
        response = super().dispatch(request, *args, **kwargs)

        return response
    
    def initialize_handlers(self):
        """Khởi tạo comment_handler và like_handler"""
        self.comment_handler = CommentViews(user_id=self.user_id)
        self.like_handler = LikeViews(user_id=self.user_id)

class PostAllCategory(PostsViews):
    def get(self, request):
        """
        Hiển thị tất cả các danh mục (category) bài viết
        Input:
            request (HttpRequest): Yêu cầu HTTP để xử lý hiển thị trang danh mục
        Output:
            HttpResponse: Trả về trang HTML 'all_category.html' với tất cả các danh mục có trong hệ thống 
            và các thông tin của người dùng
        """
        context = {
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        return render(request, 'all_category.html', context)

class PostOfCategory(PostsViews):
    def get(self, request, **kwargs):
        """
        Hiển thị tất cả bài viết thuộc một danh mục cụ thể
        Input:
            request (HttpRequest): Yêu cầu HTTP để xử lý hiển thị bài viết của danh mục.
            kwargs (dict): Từ khóa 'category_name' chứa tên danh mục cần hiển thị.
        Output:
            HttpResponse: Trả về trang HTML 'category.html' với các bài viết 'Đang hoạt động' thuộc danh mục
            và thông tin liên quan đến số lượng bình luận, lượt thích, và trạng thái "đã thích" của người dùng
        """
        category_name = kwargs.get('category_name')
        posts = Post.objects.filter(category=category_name, status='Đang hoạt động')
        post_data = []
        if posts.exists():
            post_data = list(map(lambda post: {
                'post': post,
                'total_post_comments': self.comment_handler.get_post_total_comments(post),
                'total_post_likes': self.like_handler.get_post_total_likes(post),
                'is_liked_by_user': self.like_handler.user_liked_post(post_id=post.id),
            }, posts))

        context = {
            'posts': post_data,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        return render(request, 'category.html', context)

class PostLoadAllPost(PostsViews):    
    def get(self, request):
        """
        Hiển thị tất cả các bài viết đang hoạt động cho người dùng
        Input:
            request (HttpRequest): Yêu cầu HTTP để xử lý hiển thị các bài viết
        Output:
            HttpResponse: Trả về trang HTML 'posts.html' với danh sách các bài viết đang hoạt động cùng với tổng số bình luận,
            lượt thích, và trạng thái "liked" của người dùng đối với mỗi bài viết
        """
        posts = Post.objects.filter(status='Đang hoạt động')

        post_data = list(map(lambda post: {
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked_by_user': self.like_handler.user_liked_post(post.id),
            'post': post,
        }, posts))

        context = {
            'posts': post_data,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }
        
        return render(request, 'posts.html', context)
    
class UserLoadAuthorPosts(UserViews):
    """
    Hiển thị tất cả các bài viết của tác giả với tên tác giả được cung cấp trong URL
    Input:
        request (HttpRequest): Yêu cầu HTTP để xử lý việc hiển thị các bài viết
        kwargs (dict): Tham số chứa tên tác giả từ URL
    Output:
        HttpResponse: Trả về trang HTML 'author_posts.html' với danh sách bài viết của tác giả và các thông tin liên quan
    """
    def get(self, request, **kwargs):
        author = kwargs.get('author')
        posts = Post.objects.filter(name=author, status='Đang hoạt động')

        post_data = list(map(lambda post: {
            'total_comments': self.comment_handler.get_post_total_comments(post),
            'total_likes': self.like_handler.get_post_total_likes(post),
            'is_liked': self.like_handler.user_liked_post(post.id),
            'post': post
        }, posts))

        context = {
            'posts': post_data,
            'author': author,
            'user_id': self.user_id,
            'user_name': self.user_name,
        }  

        return render(request, 'author_posts.html', context)

class PostViewPost(PostsViews):
    def get(self, request, **kwargs):
        """
        Hiển thị một bài viết với ID xác định cho người dùng
        Input:
            request (HttpRequest): Yêu cầu HTTP để xử lý việc hiển thị bài viết
            kwargs (dict): Tham số chứa ID bài viết từ URL
        Output:
            HttpResponse: Trả về trang HTML 'view_post.html' với nội dung bài viết và các thông tin liên quan
        """
        post_id = kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        context = {}
        if post.status == 'Đang hoạt động':
            context = {
                'post': post,
                'all_comments': self.comment_handler.get_all_comments(post_id),
                'user_name': self.user_name,
                'user_id': self.user_id,
                'user_comments': self.comment_handler.get_user_comments_of_post(post_id),
                'total_post_comments': self.comment_handler.get_post_total_comments(post),
                'total_post_likes': self.like_handler.get_post_total_likes(post),
                'user_liked': self.like_handler.user_liked_post(post.id),
            }
        return render(request, 'view_post.html', context)
    
    def post(self, request, **kwargs):
        """
        Cho phép người dùng thêm, sửa, hoặc xóa bình luận trên bài viết
        Input:
            request (HttpRequest): Yêu cầu HTTP để xử lý các thao tác bình luận
            kwargs (dict): Tham số chứa ID bài viết từ URL
        Output:
            HttpResponse: Trả về trang HTML 'view_post.html' với các thông tin cập nhật sau khi người dùng thực hiện các thao tác
        """
        post_id = kwargs.get('post_id')
        message = ''
        post = Post.objects.get(id=post_id, status='Đang hoạt động')
        edit_comment = None
        if request.method == 'POST' and self.user_id:
            if 'add_comment' in request.POST:
                comment = request.POST.get('comment')
                self.comment_handler.add_comment(post=post, comment_text=comment, user=self.user)
                
            elif 'edit_comment' in request.POST:
                edit_comment_id = request.POST.get('edit_comment_id')
                comment_edit_box = request.POST.get('comment_edit_box')
                self.comment_handler.edit_comment(comment_id=edit_comment_id, comment_text=comment_edit_box)
                return redirect('view_post', post_id=post_id)

            elif 'delete_comment' in request.POST:
                delete_comment_id = request.POST.get('comment_id')
                if self.comment_handler.delete_comment(comment_id=delete_comment_id, user_id=self.user_id):
                    message = "Comment deleted successfully!"

            elif 'open_edit_box' in request.POST:
                comment_id = request.POST.get('comment_id')
                comment_id = str(comment_id).strip()
                edit_comment = Comment.objects.filter(id=comment_id).first()

        context = {
            'post': post,
            'all_comments': self.comment_handler.get_all_comments(post_id),
            'user_name': self.user_name,
            'user_id': self.user_id,
            'user_comments': self.comment_handler.get_user_comments_of_post(post_id),
            'comment_id': comment_id if 'comment_id' in locals() else None,
            'edit_comment': edit_comment,
            'total_post_comments': self.comment_handler.get_post_total_comments(post),
            'total_post_likes': self.like_handler.get_post_total_likes(post),
            'user_liked': self.like_handler.user_liked_post(post.id),
            'message': message
        }
        return render(request, 'view_post.html', context)