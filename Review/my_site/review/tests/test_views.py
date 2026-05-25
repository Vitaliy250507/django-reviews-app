from django.test import TestCase
from ..models import Restaurant, Review, Profile
from django.contrib.auth.models import User
from django.urls import reverse

class RestaurantListViewTests(TestCase):
    def setUp(self):
        self.r1 = Restaurant.objects.create(name="Pizza Hut", address="Kyiv")
        self.r2 = Restaurant.objects.create(name="Sushi Master", address="Lviv")
        
    def test_base_view(self):
        response = self.client.get(reverse('review-home'))
        self.assertEqual(response.status_code, 200)
    
    def test_restaurant_list_no_filter(self):
        response = self.client.get(reverse('restaurants'), 200)
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
        