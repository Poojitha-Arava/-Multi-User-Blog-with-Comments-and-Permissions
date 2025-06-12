from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/new/', views.post_create, name='post-create'),
    path('post/<int:pk>/update/', views.post_update, name='post-update'),
    path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
    path('my-posts/', views.user_posts, name='user-posts'),
    
    # Admin URLs
    path('post-approval/', views.post_approval, name='post-approval'),
    path('post/<int:pk>/approve/', views.approve_post, name='approve-post'),
    path('post/<int:pk>/reject/', views.reject_post, name='reject-post'),
    path('post/<int:pk>/admin-delete/', views.admin_delete_post, name='admin-delete-post'),
]