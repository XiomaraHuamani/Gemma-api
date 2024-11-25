from rest_framework.viewsets import ModelViewSet
from .models import Blog
from .serializers import BlogSerializer

class BlogViewSet(ModelViewSet):
    queryset = Blog.objects.all().order_by('-created_at')
    serializer_class = BlogSerializer
