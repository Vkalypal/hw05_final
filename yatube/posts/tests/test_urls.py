from django.test import TestCase, Client
from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName1')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls(self):
        urls = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/HasNoName/': 200,
            '/create/': 302,
            '/unexisting_page/': 404,
        }
        for url, status_code in urls.items():
            with self.subTest(url=url, status_code=status_code):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_posts_post_id(self):
        post_id = self.post.id
        response = self.guest_client.get(f'/posts/{post_id}/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id_edit(self):
        post_id = self.post.id
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, 302)

    def test_unpage(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
