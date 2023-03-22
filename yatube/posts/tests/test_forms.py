from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, User


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName1')
        cls.another_user = User.objects.create_user(username='HasNoName2')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post_with_image = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с картинкой',
            image=cls.uploaded
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_with_image_on_home_page(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertContains(response, '<img')

    def test_post_with_image_on_profile_page(self):
        response = self.guest_client.get(
            reverse('posts:profile', args=[self.user]))
        self.assertContains(response, '<img')

    def test_post_with_image_on_group_page(self):
        response = self.guest_client.get(
            reverse('posts:group_list', args=[self.group.slug]))
        self.assertContains(response, '<img')

    def test_post_with_image_on_post_detail_page(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', args=[self.post_with_image.id]))
        self.assertContains(response, '<img')

    def test_create_post(self):
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:profile', args=[self.user.username])
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertEqual(self.post.text, 'Тестовый пост')

        self.assertEqual(self.group.title, 'Тестовый заголовок')

    def test_post_edit(self):
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.text, 'Отредактированный текст поста')
        self.assertEqual(self.post.group, self.group)

    def test_create_post_quest(self):
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id
        }

        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_quest(self):
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_edit_not_author(self):
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }

        self.authorized_client.force_login(self.another_user)
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/posts/1/')


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user',
                                            password='password')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_comments(self):
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id])
        )
        self.assertContains(response, form_data['text'])

    def test_comment_appears_on_post(self):
        self.client.login(username=self.user.username, password='password')
        response = self.client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data={'text': 'Test comment', 'csrfmiddlewaretoken': 'dummy_token'}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertContains(response, 'Test comment')
