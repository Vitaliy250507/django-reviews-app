from django.test import TestCase
from ..models import Restaurant, Review, Profile
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages

class RestaurantListViewTests(TestCase):
    def setUp(self):
        self.r1 = Restaurant.objects.create(name="Pizza Hut", address="Kyiv")
        self.r2 = Restaurant.objects.create(name="Sushi Master", address="Lviv")
        
    def test_base_view(self):
        response = self.client.get(reverse('review-home'))
        self.assertEqual(response.status_code, 200)
    
    def test_restaurant_list_no_filter(self):
        response = self.client.get(reverse('restaurants')) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pizza Hut')
        self.assertContains(response, 'Sushi Master')

    def test_restaurant_search(self):
        response = self.client.get(reverse('restaurants'), {'q':'Pizza'})
        self.assertContains(response, 'Pizza Hut')
        self.assertNotContains(response, 'Sushi Master')

    def test_restaurant_top(self):
        user = User.objects.create(username='Testuser')
        Review.objects.create(restaurant=self.r1, user=user, rating=5, text='Top')
        response = self.client.get(reverse('restaurants'), {'top':'true'})
        self.assertContains(response, 'Pizza Hut')
        self.assertNotContains(response, 'Sushi Master')


class RestaurantDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="vitaliy", password="123")
        self.restaurant = Restaurant.objects.create(name="Пузата Хата", address="Київ")
        self.url = reverse('restaurant-detail', kwargs={'pk': self.restaurant.pk})

    def test_get_context_data(self):
        self.client.login(username="vitaliy", password='123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context) 
        self.assertIn('allreviews', response.context)
    
    def test_post_review_already_exists(self):
        self.client.login(username='vitaliy', password='123')
        Review.objects.create(restaurant=self.restaurant, user=self.user, rating=5, text="Один")
        response = self.client.post(self.url, {'rating':'4', 'text': 'Другий'})
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Ви вже залишили відгук для цього закладу. Дякуємо!")

    def test_post_review_success(self):
        self.client.login(username="vitaliy", password="123")
        data = {
            'rating': 5,
            'text': 'Неймовірно смачно'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.url)
        self.assertTrue(Review.objects.filter(text='Неймовірно смачно').exists())

    def test_post_review_invalid(self):
        self.client.login(username="vitaliy", password="123")
        response = self.client.post(self.url, {'rating': '', 'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
