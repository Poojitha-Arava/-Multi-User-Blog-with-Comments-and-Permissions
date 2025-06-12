from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm

def is_admin(user):
    return user.is_staff

def post_list(request):
    query = request.GET.get('q')
    post_list = Post.objects.filter(status='approved').order_by('-created_at')
    
    if query:
        post_list = post_list.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    paginator = Paginator(post_list, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': query,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        if post.status != 'approved':
            messages.error(request, 'You cannot comment on unapproved posts.')
            return redirect('post-detail', pk=post.pk)
            
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('post-detail', pk=post.pk)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def user_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    context = {
        'posts': posts,
    }
    return render(request, 'blog/user_posts.html', context)

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = 'pending'
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('user-posts')
    else:
        form = PostForm()
    
    context = {
        'form': form,
    }
    return render(request, 'blog/post_form.html', context)

@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if post.status != 'draft' and post.status != 'rejected':
        messages.error(request, 'You can only edit draft or rejected posts.')
        return redirect('user-posts')
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.status = 'pending' if request.POST.get('submit_for_review') else 'draft'
            post.save()
            messages.success(request, 'Your post has been updated!')
            return redirect('user-posts')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'blog/post_form.html', context)

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted!')
        return redirect('user-posts')
    
    context = {
        'post': post,
    }
    return render(request, 'blog/post_confirm_delete.html', context)

@user_passes_test(is_admin)
def post_approval(request):
    pending_posts = Post.objects.filter(status='pending').order_by('-created_at')
    context = {
        'pending_posts': pending_posts,
    }
    return render(request, 'blog/admin/post_approval.html', context)


@user_passes_test(is_admin)
def approve_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = 'approved'
    post.save()
    post.send_approval_notification(request)  # Pass the request object
    messages.success(request, 'Post has been approved!')
    return redirect('post-approval')

@user_passes_test(is_admin)
def reject_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = 'rejected'
    post.save()
    messages.success(request, 'Post has been rejected!')
    return redirect('post-approval')

@user_passes_test(is_admin)
def admin_delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post has been deleted!')
        return redirect('post-approval')
    
    context = {
        'post': post,
    }
    return render(request, 'blog/admin/post_confirm_delete.html', context)