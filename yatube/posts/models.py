from django.db import models
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        user = User.objects.create(username='testuser')
        group = Group.objects.create(title='Test Group', slug='test-group')
        post = Post.objects.create(author=user, group=group, text='Test Post')
        self.assertEqual(post.__str__(), post.text[:15])
        self.assertEqual(group.__str__(), group.title)


class Group(models.Model):
    title = models.CharField(verbose_name='название группы', max_length=200)
    slug = models.SlugField(verbose_name='url адрес', unique=True)
    description = models.TextField(verbose_name='описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='текст поста')
    pub_date = models.DateTimeField('published_date_post', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='group_name',
        verbose_name='имя группы'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey('posts.Post',
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.post.id)])


class Follow(models.Model):
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(get_user_model(),
                               on_delete=models.CASCADE,
                               related_name='following')
