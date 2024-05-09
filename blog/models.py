from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField


class Profile(models.Model):

    full_name = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="profile")
    bio = models.TextField(null=True, blank=True)
    twitter = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.full_name)

class PostManager(models.Manager):
        paginate_by = 40
        def get_queryset(self):
            return super().get_queryset() .filter(status=Article.StatusType.PUBLISHED, type=Article.Type.POST)


class PageManager(models.Manager):

        def get_queryset(self):
            return super().get_queryset() .filter(status=Article.StatusType.PUBLISHED, type=Article.Type.PAGE)


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=120, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)
    meta_description = models.TextField(null=True, blank=True, max_length=170, verbose_name="Mô tả Meta")
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE, related_name='children', verbose_name="Danh mục cha")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "danh mục"
        verbose_name_plural = "Categories"
        db_table = "blog_categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={'slug': self.slug})


class Article(models.Model):

    class Type(models.IntegerChoices):
        POST = 1, 'Post'
        PAGE = 2, 'Page'

    class StatusType(models.IntegerChoices):
        DRAFT = 1, 'Ẩn'
        PUBLISHED = 2, 'Hiển thị'

    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = Article.Type.POST
        super(Article, self).__init__(*args, **kwargs)
    
    title = models.CharField(max_length=200, verbose_name="Tiêu đề (Title)")
    slug = models.SlugField(max_length=250, unique=True, unique_for_date='publishedAt')
    tags = models.ManyToManyField(Tag, blank=True)
    featured = models.BooleanField(default=False, verbose_name="Nổi bật (Featured)")
    excerpt = models.TextField(null=True, blank=True, default="", verbose_name="Mô tả ngắn (Excerpt)")
    featured_image = models.ImageField(null=True, blank=True, upload_to="article", default="placeholder.png", verbose_name="Hình ảnh nổi bật (Featured image)")
    body = RichTextUploadingField(null=True, blank=True, verbose_name="Nội dung (Body)")
    type = models.IntegerField('Type', blank=False, null=False, choices=Type.choices, default=Type.POST, db_column='type')
    publishedAt = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo (PublishedAt)")
    status = models.IntegerField('Trạng thái (Status)', blank=False, null=False, choices=StatusType.choices, default=StatusType.PUBLISHED, db_column='status')
    meta_title = models.CharField(null=True, blank=True,max_length=200, verbose_name="Tiêu đề SEO (SEO title)")
    meta_description = models.TextField(null=True, blank=True,max_length=500, verbose_name="Mô tả SEO (SEO description)")
    meta_keywords = models.CharField(null=True, blank=True,max_length=170, verbose_name="Từ khóa SEO (SEO keywords)")
    meta_canonical = models.CharField(null=True, blank=True,max_length=200, verbose_name="Canonical SEO (SEO canonical)")
    headscript = models.TextField(null=True, blank=True, verbose_name="Script đầu SEO (Headscript)")
    footerScript = models.TextField(blank=True)

    related_pages = models.TextField(null=True, blank=True, help_text="(Có thể nhập nhiều related pages, mỗi related pages cách nhau bởi một lần xuống dòng. Cú pháp: Tiêu đề|Link)", verbose_name="Các trang liên quan")
    objects = models.Manager()  # default manager
    pageManager = PageManager()  # custom manager
    postManager = PostManager()  # post manager
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='category', blank=True, null=True, verbose_name="Danh mục (Category)")
    store_config = models.JSONField(null=True, blank=True, help_text="field for sim page adv query")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user', blank=True, null=True, verbose_name= "Người tạo")

    def get_absolute_url(self):
        return reverse('blog:article', args=[self.slug])

    class Meta:
        ordering = ('-publishedAt',)
        db_table="blog_article"
        verbose_name = "bài viết"

    def __str__(self):
        return self.title
    
class ArticlePage(Article):
    class Meta:
        proxy = True
        verbose_name="seo page"
    def __init__(self, *args, **kwargs):
        self._meta.get_field('type').default = Article.Type.PAGE
        super(Article, self).__init__(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("blog:article", kwargs={'slug': self.slug})


