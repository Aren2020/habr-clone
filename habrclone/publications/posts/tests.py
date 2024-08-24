from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch
from ..models import User, Content, Text
from .models import Post

class PostTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username = 'User',
            password = 'User'
        )

        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        self.post = Post.objects.create( author = self.user )
        post2 = Post.objects.create( author = self.user )
        
        text = Text.objects.create( creator = self.user, content = 'text item')
        Content.objects.create(
            publication = self.post,
            item = text
        )

        self.post_list_url = reverse('publications:posts:list')
        self.post_edit_url = reverse('publications:posts:edit', kwargs = {'post_id': self.post.id})
    
    
    @patch('publications.posts.views.post_service.r')
    def test_post_list(self, mock_obj):
        mock_obj.return_value = b'0' # mock redis

        res = self.client.get(self.post_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)
        for post in res.data:
            items = post.get('items')
            if post.get('id') == self.post.id:
                self.assertEqual( len(items), 1)
            else:
                self.assertEqual( len(items), 0)

    @patch('publications.articles.views.article_service.r')
    def test_create_article(self, mock_obj):
        mock_obj.return_value = b'0' # mock redis

        res = self.client.post(self.post_list_url, { 'mention': [1] })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Post.objects.all().count(), 3)

        res = self.client.post(self.post_list_url)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.data.keys()), set(['mention']))
    
    def test_bad_user(self):
        user = User.objects.create(
            username = 'Bad',
            password = 'User'
        )
        access_token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        res_get = self.client.delete(self.post_edit_url)
        self.assertEqual(res_get.status_code, 403)

        res_put = self.client.put(self.post_edit_url)
        self.assertEqual(res_put.status_code, 403)

        res_delete = self.client.delete(self.post_edit_url)
        self.assertEqual(res_delete.status_code, 403)
    
    
    def test_bad_publication(self):
        post_bad_url = reverse('publications:posts:edit', kwargs = {'post_id': self.post.id + 454})

        res_get = self.client.delete(post_bad_url)
        self.assertEqual(res_get.status_code, 404)

        res_put = self.client.put(post_bad_url)
        self.assertEqual(res_put.status_code, 404)

        res_delete = self.client.delete(post_bad_url)
        self.assertEqual(res_delete.status_code, 404)

    
    def test_post_edit(self):
        post_edit_data = {
            'mention': [self.user.id],
            'status': 0
        }

        post_data = self.client.get(self.post_edit_url)
        self.assertEqual(post_data.status_code, 200)
        self.assertEqual(set(post_data.data.keys()), set(['mention', 'status']))        

        res = self.client.put(self.post_edit_url, post_edit_data)
        self.assertEqual(res.status_code, 204)
        self.post.refresh_from_db()
        self.assertTrue(self.user in self.post.mention.all())
        self.assertFalse(self.post.status)
    
        post_delete = self.client.delete(self.post_edit_url)
        self.assertEqual(post_delete.status_code, 204)
        self.assertFalse( Post.objects.filter(id = self.post.id).exists() )

# git stash test