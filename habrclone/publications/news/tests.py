from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch
from ..models import User, Content, Text
from .models import News

class NewsTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create(
            username = 'User',
            password = 'User'
        )

        access_token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION = f'Bearer {access_token}')

        news_data = {
            'author': self.user,
            'intro_image': None,
            'intro_text': 'intro_text',
            'title': 'Title'
        }
        self.news = News.objects.create( **news_data )
        News.objects.create( **news_data )
        
        text = Text.objects.create( creator = self.user, content = 'text item')
        Content.objects.create(
            publication = self.news,
            item = text
        )

        self.news_list_url = reverse('publications:news:list')
        self.news_detail_url = reverse('publications:news:detail', kwargs = {'news_id': self.news.id})
        self.news_edit_url = reverse('publications:news:edit', kwargs = {'news_id': self.news.id})
    
    
    @patch('publications.news.views.news_service.r')
    def test_news_list(self, mock_obj):
        mock_obj.return_value = b'0' # mock redis

        res = self.client.get(self.news_list_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)
    
    
    @patch('publications.news.views.news_service.r')
    def test_detail_list(self, mock_obj):
        mock_obj.return_value = b'0' # mock redis

        res = self.client.get(self.news_detail_url)
        items = res.data.get('items')
        if res.data.get('id') == self.news.id:
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

        res_get = self.client.delete(self.news_edit_url)
        self.assertEqual(res_get.status_code, 403)

        res_put = self.client.put(self.news_edit_url)
        self.assertEqual(res_put.status_code, 403)

        res_delete = self.client.delete(self.news_edit_url)
        self.assertEqual(res_delete.status_code, 403)
    
    
    def test_bad_publication(self):
        news_bad_url = reverse('publications:news:edit', kwargs = {'news_id': self.news.id + 454})

        res_get = self.client.delete(news_bad_url)
        self.assertEqual(res_get.status_code, 404)

        res_put = self.client.put(news_bad_url)
        self.assertEqual(res_put.status_code, 404)

        res_delete = self.client.delete(news_bad_url)
        self.assertEqual(res_delete.status_code, 404)

    
    def test_news_edit(self):
        news_edit_data = {
            'mention': [self.user.id],
            'status': 0,
            'tags': ['tago'],
            'intro_image': '',
            'intro_text': 'intro_text',
            'title': 'Title'
        }

        news_data = self.client.get(self.news_edit_url)
        self.assertEqual(news_data.status_code, 200)
        self.assertEqual(set(news_data.data.keys()), set(news_edit_data.keys()))        

        res = self.client.put(self.news_edit_url, news_edit_data)
        self.assertEqual(res.status_code, 204)

        self.news.refresh_from_db()
        self.assertTrue(self.user in self.news.mention.all())
        self.assertFalse(self.news.status)        
        self.assertTrue('tago' in self.news.tags.values_list('slug', flat = True))

        news_delete = self.client.delete(self.news_edit_url)
        self.assertEqual(news_delete.status_code, 204)
        self.assertFalse( News.objects.filter(id = self.news.id).exists() )
