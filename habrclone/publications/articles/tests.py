from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch
from ..models import User, Content, Text
from .models import Article

class ArticleTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username = 'User',
            password = 'User'
        )

        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        article_data = {
            'author': self.user,
            'intro_image': None,
            'intro_text': 'intro_text',
            'title': 'Title',
            'level': 'easy'
        }
        self.article = Article.objects.create( **article_data )
        Article.objects.create( **article_data )
        
        text = Text.objects.create( creator = self.user, content = 'text item')
        Content.objects.create(
            publication = self.article,
            item = text
        )

        self.article_list_url = reverse('publications:articles:list')
        self.article_detail_url = reverse('publications:articles:detail', kwargs = {'article_id': self.article.id})
        self.article_edit_url = reverse('publications:articles:edit', kwargs = {'article_id': self.article.id})
    
    
    @patch('publications.articles.views.article_service.r')
    def test_article_list(self, mock_obj):
        mock_obj.return_value = b'0' # mock redis

        res = self.client.get(self.article_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.data) <= 4)
    
    
    @patch('publications.articles.views.article_service.r')
    def test_detail_list(self, mock_obj):
        mock_obj.return_value = b'0' # mock redis

        res = self.client.get(self.article_detail_url)
        items = res.data.get('items')
        if res.data.get('id') == self.article.id:
            self.assertEqual( len(items), 1)
        else:
            self.assertEqual( len(items), 0)

    
    def test_bad_user(self):
        user = User.objects.create(
            username = 'Bad',
            password = 'User'
        )
        access_token = AccessToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        res_get = self.client.delete(self.article_edit_url)
        self.assertEqual(res_get.status_code, 403)

        res_put = self.client.put(self.article_edit_url)
        self.assertEqual(res_put.status_code, 403)

        res_delete = self.client.delete(self.article_edit_url)
        self.assertEqual(res_delete.status_code, 403)
    
    
    def test_bad_publication(self):
        article_bad_url = reverse('publications:articles:edit', kwargs = {'article_id': self.article.id + 454})

        res_get = self.client.delete(article_bad_url)
        self.assertEqual(res_get.status_code, 404)

        res_put = self.client.put(article_bad_url)
        self.assertEqual(res_put.status_code, 404)

        res_delete = self.client.delete(article_bad_url)
        self.assertEqual(res_delete.status_code, 404)

    
    def test_article_edit(self):
        article_edit_data = {
            'mention': [self.user.id],
            'status': 0,
            'tags': ['tago'],
            'intro_image': '',
            'intro_text': 'intro_text',
            'title': 'Title',
            'level': 'hard'
        }

        article_data = self.client.get(self.article_edit_url)
        self.assertEqual(article_data.status_code, 200)
        self.assertEqual(set(article_data.data.keys()), set(article_edit_data.keys()))        

        res = self.client.put(self.article_edit_url, article_edit_data)
        self.assertEqual(res.status_code, 204)

        self.article.refresh_from_db()
        self.assertTrue(self.user in self.article.mention.all())
        self.assertFalse(self.article.status)
        self.assertEqual(self.article.level, 'hard')     
        self.assertTrue('tago' in self.article.tags.values_list('slug', flat = True))

        article_delete = self.client.delete(self.article_edit_url)
        self.assertEqual(article_delete.status_code, 204)
        self.assertFalse( Article.objects.filter(id = self.article.id).exists() )
