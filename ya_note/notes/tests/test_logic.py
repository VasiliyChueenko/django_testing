
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.urls import reverse


from pytils.translit import slugify


from notes.models import Note
from notes.forms import WARNING
from .common import CommonTestCase

User = get_user_model()


class TestRoutes(CommonTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        url = reverse('notes:add')
        response = self.author_client.post(url, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.data['title'])
        self.assertEqual(new_note.text, self.data['text'])
        self.assertEqual(new_note.slug, self.data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        Note.objects.all().delete()
        url = reverse('notes:add')
        response = self.client.post(url, self.data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:add')
        response = self.author_client.post(url, data={
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': self.note.slug
        })
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        Note.objects.all().delete()
        url = reverse('notes:add')
        self.data.pop('slug')
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_delete_note(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.author_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.data)
        self.assertRedirects(response, reverse('notes:success'))
        edited_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(edited_note.title, self.data['title'])
        self.assertEqual(edited_note.text, self.data['text'])
        self.assertEqual(edited_note.slug, self.data['slug'])

    def test_other_user_cant_edit_note(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.author,
        )
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_user_client.post(url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        edited_note = Note.objects.get(pk=self.note.pk)
        self.assertNotEqual(edited_note.title, self.data['title'])
        self.assertNotEqual(edited_note.text, self.data['text'])
        self.assertNotEqual(edited_note.slug, self.data['slug'])
