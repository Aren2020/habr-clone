from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
from django.urls import reverse
from publications.posts.models import Post
from users.models import User
from .models import Content, Text

class ContentTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username = 'Ryan',
            password = 'Ryano'
        )
        post = Post.objects.create( author = self.user )
        post.mention.add(self.user)

        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')
        
        self.content_create_text_url = reverse('publications:content_create', 
                                          kwargs = {'publication_type': 'posts',
                                                    'publication_id': post.id,
                                                    'model_name': 'text'})

        self.bad_publication_url = reverse('publications:content_create',
                                           kwargs = {'publication_type': 'posts',
                                                     'publication_id': post.id + 1,
                                                     'model_name': 'text'})

    def test_bad_publication(self):
        res = self.client.post(self.bad_publication_url)
        self.assertEqual(res.status_code, 404)

    def test_bad_user(self):
        user = User.objects.create(
            username = 'Bad',
            password = 'User'
        )
        access_token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')
        
        res = self.client.post(self.content_create_text_url)
        self.assertEqual(res.status_code, 403)

    def test_create_content_invalid(self):
        res = self.client.post(self.content_create_text_url, {})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(len(res.data), 1)

    def test_create_text_content(self): # this is enough for testing the algorithm is the same for all type of items
        text_valid_content = { 'content': 'Text' }
        res = self.client.post(self.content_create_text_url, text_valid_content)
        self.assertEqual(res.status_code, 204)
        self.assertTrue(Content.objects.count(), 1)

class ItemTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username = 'Ryan',
            password = 'Ryano'
        )
        post = Post.objects.create( author = self.user )
        post.mention.add(self.user)
        self.text = Text.objects.create( creator = self.user, content = 'Text1' )
        Content.objects.create(
            publication = post,
            item = self.text
        )

        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        self.item_edit_url = reverse('publications:item_detail',
                                     kwargs = {'model_name': 'text',
                                               'item_id': self.text.id})

    def test_bad_user(self):
        self.user = User.objects.create(
            username = 'Bad',
            password = 'User'
        )
        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        post = Post.objects.create( author = self.user )
        post.mention.add(self.user)

        res = self.client.get(self.item_edit_url)
        self.assertEqual(res.status_code, 403)

    def test_edit_invalid(self):
        res = self.client.put(self.item_edit_url, {})
        self.assertEqual(res.status_code, 400)

    def test_delete_bad_item(self):        
        text = Text.objects.create( creator = self.user, content = 'Bad item' ) # No content for this item
        item_delete_bad_url = reverse('publications:item_detail',
                                     kwargs = {'model_name': 'text',
                                               'item_id': text.id})
        
        res = self.client.delete(item_delete_bad_url)
        self.assertEqual(res.status_code, 404)
        
    def test_text_item_edit_get(self):
        res = self.client.get(self.item_edit_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(set(res.data.keys()), set(['item_name', 'content']))

    def test_text_item_put(self):
        text_valid_content = { 'content': 'Textulo' }
        res = self.client.put(self.item_edit_url, text_valid_content)
        self.assertEqual(res.status_code, 204)

        self.text.refresh_from_db()
        self.assertEqual(self.text.content, text_valid_content['content'])

    def test_text_item_delete(self):   
        res = self.client.delete(self.item_edit_url)
        self.assertEqual(res.status_code, 204)
        self.assertEqual(Content.objects.count(), 0)
        self.assertFalse(Text.objects.filter(id = self.text.id).exists())

