from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
    
    def send_approval_notification(self, request=None):
        if self.status == 'approved':
            subject = f'Your post "{self.title}" has been approved'

            if request:
                post_url = request.build_absolute_uri(
                    reverse('post-detail', kwargs={'pk': self.pk})
                )
            else:
                post_url = f"http://example.com{reverse('post-detail', kwargs={'pk': self.pk})}"

            message = f'''Hello {self.author.username},

Your post "{self.title}" has been approved and is now visible to all users.

View it here: {post_url}

Thanks,
The Blog Team
'''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.author.email],
                fail_silently=False,
            )

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'