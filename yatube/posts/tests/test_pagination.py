from django.test import Client, TestCase
from django.urls import reverse
from yatube.settings import POSTS_PER_PAGE
from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
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

        # Создаем группу и связываем с ней 13 постов
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug1'
        )
        self.posts = Post.objects.bulk_create([
            Post(author=self.user,
                 text=f'Тестовый пост {i}',
                 group=self.group
                 )
            for i in range(13)
        ])

    def test_first_page_contains_ten_records(self):
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': 'StasBasov'}),
        )
        for url in urls:
            response = self.client.get(url)
            amount_posts = len(response.context.get('page_obj').object_list)
            self.assertEqual(amount_posts, POSTS_PER_PAGE)

    def test_second_page_contains_ten_records(self):
        urls = (
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2',
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}) + '?page=2',
        )
        for url in urls:
            response = self.client.get(url)
            amount_posts = len(response.context.get('page_obj').object_list)
            self.assertEqual(amount_posts, 3)
