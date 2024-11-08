from django.shortcuts import render, redirect, get_object_or_404
from ..models import Admin, User, Post, Like, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone

from .base import BaseView

class PostsViews(BaseView):
    
    def __init__(self, request):
        super().__init__(request)

    # Hiển thị tất cả các bài viết
    def load_posts(self):
        posts = Post.objects.filter(status='active')

        post_data = []
        for post in posts:
            total_comments = Comment.objects.filter(post_id=post.id).count()
            total_likes = Like.objects.filter(post_id=post.id).count()
            is_liked = Like.objects.filter(user_id=self.user_id, post_id=post.id).exists()
            post_data.append({
                'total_comments': total_comments,
                'total_likes' : total_likes,
                'is_liked_by_user': is_liked,
                'post': post,
            })

        context = {
            'posts': post_data,
            'user_id': self.user_id,
        }
        
        return render(self.request, 'posts.html', context)

    # Hiển thị bài viết có id = post_id
    def view_post(self, post_id):
        post = Post.objects.get(id=post_id, status='active')
        edit_comment = None
        if self.request.method == 'POST' and self.user_id:
            if 'add_comment' in self.request.POST:
                comment = self.request.POST.get('comment')
                Comment.objects.create(
                    post_id=post,
                    admin_id=post.admin,
                    user_id=self.user,
                    comment=comment,
                    date=timezone.now(),
                )
            
            elif 'edit_comment' in self.request.POST:
                edit_comment_id = self.request.POST.get('edit_comment_id')
                comment_edit_box = self.request.POST.get('comment_edit_box')

                comment_to_edit = Comment.objects.filter(id=edit_comment_id).first()
                if comment_to_edit:
                    comment_to_edit.comment = comment_edit_box
                    comment_to_edit.save()
                return redirect('view_post', post_id=post_id)

            elif 'delete_comment' in self.request.POST:
                delete_comment_id = self.request.POST.get('comment_id')
                comment_to_delete = Comment.objects.filter(id=delete_comment_id).first()
                if comment_to_delete:
                    comment_to_delete.delete()

            elif 'open_edit_box' in self.request.POST:
                comment_id = self.request.POST.get('comment_id')
                comment_id = str(comment_id).strip()
                edit_comment = Comment.objects.filter(id=comment_id).first()

        all_comments = Comment.objects.filter(post_id=post_id)
        user_comments = Comment.objects.filter(user_id=self.user_id) if self.user_id else None

        total_post_comments = Comment.objects.filter(post_id=post_id).count()
        total_post_likes = Like.objects.filter(post_id=post_id).count()
        user_liked = False

        if self.user_id:
            user_liked = Like.objects.filter(post_id=post_id, user_id=self.user_id).exists()

        context = {
            'post': post,
            'all_comments': all_comments,
            'user_name': self.user_name,
            'user_id': self.user_id,
            'user_comments': user_comments,
            'comment_id': comment_id if 'comment_id' in locals() else None,
            'edit_comment': edit_comment,
            'total_post_comments': total_post_comments,
            'total_post_likes': total_post_likes,
            'user_liked': user_liked,
        }
        return render(self.request, 'view_post.html', context)

