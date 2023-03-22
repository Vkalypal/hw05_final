from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache
from posts.models import Group, Post, User, Follow


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # Создаём новый пост
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'StasBasov'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        expected = list(Post.objects.all())
        received = list(response.context['page_obj'])
        self.assertEqual(expected, received)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        posts = response.context['page_obj']
        filter_posts = Post.objects.filter(group=self.group)
        self.assertEqual(list(posts), list(filter_posts))

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'StasBasov'})
        )
        posts = response.context['page_obj']
        filter_author = Post.objects.filter(author=self.user)
        self.assertEqual(list(posts), list(filter_author))

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        posts = response.context['post']
        self.assertEqual(posts, self.post)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'form': forms.ModelForm,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertIsInstance(response.context[value], expected)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')

    def setUp(self):
        self.guet_client = Client()

    def test_chaching_index_page(self):
        response = self.guet_client.get(reverse('posts:index'))
        self.post = response.content
        Post.objects.create(
            text='cachetest',
            author=CacheTest.author
        )
        response_old = self.guet_client.get(reverse('posts:index'))
        self.old_post = response_old.content
        Post.objects.filter(
            text='cachetest',
            author=CacheTest.author
        )
        cache.clear()
        response_new = self.guet_client.get(reverse('posts:index'))
        old_post = response_old.content
        self.assertEqual(old_post, self.post)
        new_post = response_new.content
        self.assertNotEqual(old_post, new_post)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1',
                                             password='password1')
        cls.user2 = User.objects.create_user(username='user2',
                                             password='password2')
        cls.post = Post.objects.create(
            text='Test post',
            author=cls.user2
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

    def test_user_can_follow_user(self):
        response = self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user2.username}
                    ),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        follow_exists = Follow.objects.filter(
            user=self.user1, author=self.user2
        ).exists()
        self.assertTrue(follow_exists)

    def test_user_can_unfollow_user(self):
        response = self.client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user2.username}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user2 in self.user1.follower.all())
